//! A format M file's own net (`proof_net`), from jlevy/squares#366: admission
//! reads the declared step and last index in place of the standard 83/40000 and
//! 200, holds the declared net to every premise the standard one meets
//! (SOUNDNESS.md, lemma N0), and refuses a declaration it would not use, a
//! malformed one, and metadata that changes it.

use num_bigint::BigInt;
use num_rational::BigRational;
use serde_json::{Value, json};
use sqverify_fast::certificate::{Certificate, admit, direction, domain_upper};

fn ratio(p: i64, q: i64) -> BigRational {
    BigRational::new(BigInt::from(p), BigInt::from(q))
}

fn text(q: &BigRational) -> String {
    format!("{}/{}", q.numer(), q.denom())
}

fn admit_value(value: &Value, n: u64) -> Result<Certificate, String> {
    let raw = value.to_string().into_bytes();
    admit(&raw, value, n, None).map_err(|error| error.0)
}

/// A format M file with one row, core `b` and the given `proof_net`, if any.
fn mixed(b: &str, net: Option<Value>) -> Value {
    let mut value = json!({"n": 2, "L": "3", "B": b, "points": [],
        "rectangles": [{"rectangle": [0, 0, 1, 1], "mass": 1}]});
    if let Some(net) = net {
        value["proof_net"] = net;
    }
    value
}

/// The net of `mixed_n18_L470`: step 1/1001, 416 nodes.
fn fine() -> Value {
    json!({"step": "1/1001", "last": 415})
}

#[test]
fn a_declared_net_replaces_the_standard_one() {
    let cert = admit_value(&mixed("999/1000", Some(fine())), 2).expect("admitted");
    assert_eq!(cert.step, ratio(1, 1001));
    assert_eq!(cert.angle_count, 416);
    assert_eq!(cert.net_origin, "proof_net");
    assert_eq!(cert.format, "M");
    // The last direction is the declared net's, t = 415/1001.
    let t = ratio(415, 1001);
    let one = ratio(1, 1);
    let (c, s) = direction(&cert.step, 415);
    assert_eq!(c, (&one - &t * &t) / (&one + &t * &t));
    assert_eq!(s, ratio(2, 1) * &t / (&one + &t * &t));
    // The per-bin domain uses the declared half-step: a_r = t_r - 1/2002.
    let rho = |a: &BigRational| (&one + ratio(2, 1) * a - a * a) / (ratio(2, 1) * (&one + a * a));
    for index in [0u32, 1, 207, 415] {
        let t = ratio(i64::from(index), 1001);
        let a = if t > ratio(1, 2002) {
            t - ratio(1, 2002)
        } else {
            ratio(0, 1)
        };
        assert_eq!(domain_upper(&cert, index).unwrap(), ratio(3, 1) - rho(&a));
    }
    // A count restated as last + 1 is the same declaration.
    let restated = json!({"step": "1/1001", "last": 415, "count": 416});
    assert!(admit_value(&mixed("999/1000", Some(restated)), 2).is_ok());
    // The standard net, declared, is admitted as itself.
    let standard = json!({"step": "83/40000", "last": 200});
    let cert = admit_value(&mixed("9977/10000", Some(standard)), 2).expect("admitted");
    assert_eq!((cert.step, cert.angle_count), (ratio(83, 40000), 201));
}

#[test]
fn without_its_declaration_the_core_does_not_fit_the_standard_net() {
    // B = 999/1000 needs the finer net: B (1 + 83/40000) > 1.
    let error = admit_value(&mixed("999/1000", None), 2).unwrap_err();
    assert!(error.contains("B (1 + D)"), "{error}");
}

#[test]
fn a_corrupted_declaration_is_refused() {
    let variants: [(&str, Value, &str); 18] = [
        // B (1 + D) = 999/1000 * 1000/999 = 1 exactly: the core need not fit.
        (
            "step 1/999",
            json!({"step": "1/999", "last": 415}),
            "B (1 + D)",
        ),
        // t_414 = 414/1001 < tan(pi/8): the net stops short of pi/4.
        ("last 414", json!({"step": "1/1001", "last": 414}), "pi/4"),
        // t_max = 600/1001 > 1/2: lemma F3's cap.
        ("last 600", json!({"step": "1/1001", "last": 600}), "1/2"),
        (
            "step zero",
            json!({"step": "0", "last": 415}),
            "positive step",
        ),
        (
            "step negative",
            json!({"step": "-1/1001", "last": 415}),
            "positive step",
        ),
        (
            "step not a number",
            json!({"step": "one/1001", "last": 415}),
            "proof_net.step",
        ),
        ("step missing", json!({"last": 415}), "proof_net.step"),
        (
            "last a string",
            json!({"step": "1/1001", "last": "415"}),
            "proof_net.last",
        ),
        (
            "last fractional",
            json!({"step": "1/1001", "last": 415.5}),
            "proof_net.last",
        ),
        (
            "last negative",
            json!({"step": "1/1001", "last": -1}),
            "proof_net.last",
        ),
        (
            "count disagrees",
            json!({"step": "1/1001", "last": 415, "count": 415}),
            "count",
        ),
        (
            "a field this reader does not know",
            json!({"step": "1/1001", "last": 415, "offset": "1/2002"}),
            "does not know",
        ),
        ("not an object", json!(["1/1001", 415]), "object"),
        // One direction: the net needs at least two (lemma N0 (a)).
        ("last 0", json!({"step": "1/1001", "last": 0}), "directions"),
        // A net that reaches past pi/4, but at 414,215 directions, past F3's 2^16 cap.
        (
            "a reaching net above 2^16 directions",
            json!({"step": "1/1000000", "last": 414_214}),
            "directions",
        ),
        // 2^32: the count last + 1 leaves u32.
        (
            "last above the u32 range",
            json!({"step": "1/1001", "last": 4_294_967_296_u64}),
            "proof_net.last",
        ),
        (
            "last 2^40",
            json!({"step": "1/1001", "last": 1_099_511_627_776_u64}),
            "proof_net.last",
        ),
        // An exponent is not a JSON integer, even when its value is one.
        (
            "last in exponent form",
            serde_json::from_str(r#"{"step": "1/1001", "last": 4.15e2}"#).expect("JSON"),
            "proof_net.last",
        ),
    ];
    for (name, net, expected) in variants {
        let error = admit_value(&mixed("999/1000", Some(net)), 2)
            .expect_err(&format!("{name} was admitted"));
        assert!(error.contains(expected), "{name}: {error}");
    }
}

#[test]
fn metadata_may_restate_a_declared_net_but_never_change_it() {
    let with_metadata = |metadata: Value| {
        let mut value = mixed("999/1000", Some(fine()));
        value["certificate"] = metadata;
        value
    };
    assert!(
        admit_value(
            &with_metadata(json!({"D": "1/1001", "angle_count": 416})),
            2
        )
        .is_ok()
    );
    for metadata in [
        json!({"D": "83/40000"}),
        json!({"angle_count": 201}),
        json!({"D": "1/1000", "angle_count": 416}),
        json!({"D": "1/1001", "angle_count": 417}),
    ] {
        let error = admit_value(&with_metadata(metadata.clone()), 2)
            .expect_err(&format!("{metadata} was admitted"));
        assert!(
            error.contains("net") || error.contains("B (1 + D)"),
            "{metadata}: {error}"
        );
    }
}

#[test]
fn only_format_m_declares_a_net() {
    let tokoharu = json!({"L": "3", "B": "9/10", "rectangles": [[0, 0, 1, 1]], "weights": [1],
        "proof_net": fine()});
    let error = admit_value(&tokoharu, 2).unwrap_err();
    assert!(error.contains("proof_net"), "{error}");
    let linear = json!({"schema": "point_line_rectangle_v1", "L": "3", "B": "9/10",
        "net": {"step": "83/40000", "last": 200}, "proof_net": fine(),
        "primitives": [{"kind": "point", "geometry": [1, 1], "mass": 1}]});
    let error = admit_value(&linear, 2).unwrap_err();
    assert!(error.contains("proof_net"), "{error}");
}

#[test]
fn the_per_bin_tangent_form_is_checked_on_the_declared_step() {
    // Between the half-angle limit 1/(1 + D) and the tangent limit
    // 1/(1 + D/(1 - D^2/4)) at D = 1/1001, B passes the first and must fail the
    // second for format M (SOUNDNESS.md, N3).
    let d = ratio(1, 1001);
    let one = ratio(1, 1);
    let tangent = &d / (&one - &d * &d / ratio(4, 1));
    let half_limit = &one / (&one + &d);
    let tangent_limit = &one / (&one + &tangent);
    assert!(tangent_limit < half_limit);
    let between = (&half_limit + &tangent_limit) / ratio(2, 1);
    assert!(&between * (&one + &d) < one);
    assert!(&between * (&one + &tangent) >= one);
    let error = admit_value(&mixed(&text(&between), Some(fine())), 2).unwrap_err();
    assert!(error.contains("per-bin"), "{error}");
    // The certificate's own B = 999/1000 clears both forms.
    let b = ratio(999, 1000);
    assert!(&b * (&one + &tangent) < one);
}

#[test]
fn a_duplicate_key_inside_the_declaration_is_refused_by_the_reader() {
    // Two readers could disagree about which `last` a file declares.
    let dir = std::env::temp_dir().join(format!("sqverify-net-{}", std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    let path = dir.join("dup-net.json");
    std::fs::write(
        &path,
        r#"{"n": 2, "L": "3", "B": "999/1000", "points": [],
            "rectangles": [{"rectangle": [0, 0, 1, 1], "mass": 1}],
            "proof_net": {"step": "1/1001", "last": 415, "last": 600}}"#,
    )
    .unwrap();
    let error = sqverify_fast::certificate::read_json(&path).unwrap_err();
    assert!(error.0.contains("duplicate JSON key"), "{error}");
    std::fs::remove_dir_all(&dir).unwrap();
}

#[test]
fn a_net_block_outside_format_l_is_refused_not_ignored() {
    // Finding DN-5 of the 5 October review: format L's net block in a format M or T
    // file would otherwise be ignored.
    let mut both = mixed("999/1000", Some(fine()));
    both["net"] = json!({"step": "83/40000", "last": 200});
    let error = admit_value(&both, 2).unwrap_err();
    assert!(error.contains("net block"), "{error}");
    let standard = json!({"n": 2, "L": "3", "B": "9/10", "points": [],
        "rectangles": [{"rectangle": [0, 0, 1, 1], "mass": 1}],
        "net": {"step": "83/40000", "last": 200}});
    assert!(admit_value(&standard, 2).unwrap_err().contains("net block"));
    let tokoharu = json!({"L": "3", "B": "9/10", "rectangles": [[0, 0, 1, 1]], "weights": [1],
        "net": {"step": "83/40000", "last": 200}});
    assert!(admit_value(&tokoharu, 2).unwrap_err().contains("net block"));
}
