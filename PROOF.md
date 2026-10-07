# ZH: 密度、连续覆盖与削角转移证明
# EN: Density, continuous coverage and cap-transfer proof

ZH: 记 K=[0,L]^2，以下参数均为精确有理数；节点角 theta_r=2 atan(rD)，其余弦和正弦分别为 (1−r²D²)/(1+r²D²) 与 2rD/(1+r²D²)。
EN: Let K=[0,L]^2. All parameters below are exact rationals; node angle theta_r=2 atan(rD) has cosine (1−r²D²)/(1+r²D²) and sine 2rD/(1+r²D²).

```text
L=67/10; X=33509/5000; q=L/X=33500/33509
B=9977/10000; M=3999/100; D=83/40000
h=1019088832887/10^15; r=0,...,200
tau(0)=2503/2500
tau(1..3)=10009/10000
tau(4..33)=1251/1250
tau(34..42)=2001/2000
tau(43..200)=10001/10000
```

ZH: 对区间 r，令 d_r=D/(1+r(r+1)D²)、b_r=(d_r−h)/(1+d_r h)，端点相对角为 2 atan(b_r)。b_r>0 且 B(c(b_r)+s(b_r))>q 时需要削角上界，其余区间无需收费损失。
EN: For interval r, set d_r=D/(1+r(r+1)D²), b_r=(d_r−h)/(1+d_r h), with endpoint relative angle 2 atan(b_r). A cap bound is needed exactly when b_r>0 and B(c(b_r)+s(b_r))>q; other intervals incur no loss.

## ZH: 密度与节点命题
## EN: Density and nodal propositions

ZH: 将每个正权代表矩形的四顶点平移到容器中心，枚举坐标交换和两个符号，得到八个正交变换。每个像赋密度 w/(8 area(R))；即使像重复也计入全部质量。480 个正权代表展开为 3840 项；非负性、支持范围、四分之一转动和反射不变性以及质量 3999/100 已由新的有理数程序直接检查。
EN: Center each positive representative's four vertices and enumerate coordinate exchange and two signs, obtaining eight orthogonal maps. Assign each image density w/(8 area(R)), counting full multiplicity even for repeated images. The 480 positive representatives expand to 3840 terms; a new rational program directly checks nonnegativity, support, quarter-turn and reflection invariance, and mass 3999/100.

ZH: 固定方向 r 时，合法中心域为 [B(c_r+s_r)/2,L-B(c_r+s_r)/2]^2。容器中心的四分之一转动保持正方形方向模 π/2，足以把任何中心移到右上象限。反射改变固定方向的符号，因此不能作为此处缩域理由。
EN: At fixed direction r, legal centers form [B(c_r+s_r)/2,L-B(c_r+s_r)/2]^2. Quarter-turns about the container center preserve square orientation modulo π/2 and move any center into the upper-right quadrant. Reflection changes the sign of the fixed orientation and cannot justify this reduction.

ZH: 水平交叠长度在矩形端点加减 B/2 处才改变斜率；所有相邻断点单元上总积分是双线性函数，因而是四个角点值的凸组合。包含域边界和全部断点的扫描证明整个连续域，而非采样。原整数算法用向内取整支持和向下取整密度；第二 Rust 算法用精确事件坐标与外包斜率扫描。
EN: Horizontal overlap lengths change slope only at rectangle endpoints shifted by ±B/2. The total integral is bilinear on each adjacent-event cell and therefore a convex combination of its four vertex values. A scan including domain boundaries and every breakpoint proves the whole continuous domain, not samples. The original integer route rounds supports inward and density downward; the second Rust route uses exact event coordinates and outward slope sweeps.

ZH: 非水平两路线都使用平移积分的边界切片导数及中心盒覆盖，这是共享引理。原 C++ 以经区间核验的内接多边形下界中心面积；Rust 以凹截面函数的梯形下界计算中心面积，独立产生九项仿射边长外包。细分盒的闭并集覆盖父盒，深度或节点用尽必须拒绝。
EN: Both nonhorizontal routes use boundary-slice derivatives of translated integrals and exhaustive center boxes; these are shared lemmas. The original C++ bounds center area by interval-certified inscribed polygons; Rust uses trapezoids below a concave section function and independently generated nine-term affine edge enclosures. Closed child boxes cover their parent, and depth or node exhaustion must refuse acceptance.

## ZH: 连续角度、端点三角形与有限上界
## EN: Continuous angles, endpoint triangles, and finite bounds

ZH: 对每个父方块分别利用密度的 D4 不变性把方向折到 [0,π/4]，这是单个积分的对称性论证，不要求把不同父方块各自旋转后仍组成装填。节点 200 的半角正切 83/200 超过 √2−1，因此网格覆盖 π/4；最后一个节点略超 π/4，必须保留。
EN: Fold each parent's orientation separately into [0,π/4] using D4 invariance of its integral. This does not require independently transformed parents to form a packing. Node 200 has half-angle tangent 83/200 greater than √2−1, so the net covers π/4; the last node is slightly beyond π/4 and must remain.

ZH: 若上节点距离不超过 δ0=2 atan(h)，B(c(h)+s(h))≤q 保证该同心参考方块包含在实际父方块内。否则下节点的角误差小于相邻间隔减 δ0；下节点角度不大于父角且不超过 π/4，因此其轴向外包宽度 B(c+s) 不超过父方块的 q(cos α+sin α)，保证它仍合法处于容器内。上节点超过 π/4 不影响第一分支，因为该分支只用相对角度包含。
EN: If the upper node is within δ0=2 atan(h), B(c(h)+s(h))≤q places the concentric reference inside the actual parent. Otherwise the lower-node error is less than the adjacent gap minus δ0. The lower angle does not exceed the parent angle or π/4, so its axis-aligned extent B(c+s) is no larger than the parent's q(cos α+sin α), keeping it legally inside the container. An upper node beyond π/4 does not affect the first branch, which uses relative-angle containment only.

ZH: 有损分支下，父支持直线在参考正方形四角各削去三角形；两腿为 [B(c+s)−q]/(2c) 和 [B(c+s)−q]/(2s)。两腿对相对角度的导数符号分别由 B−q sin δ 和 q cos δ−B 控制。本次所有有损区间都精确检查了端点处的充分守卫，因此任意实际削角包含在其端点三角形内。
EN: In a lossy branch the parent support lines cut one triangle at each reference corner, with legs [B(c+s)−q]/(2c) and [B(c+s)−q]/(2s). Their derivative signs are controlled by B−q sin δ and q cos δ−B respectively. Exact endpoint guards hold in every active interval, so every actual cap lies inside its endpoint triangle.

ZH: 新程序没有用腿公式生成三角形，而是精确裁剪四个外半平面；之后验证四个正面积三角形及其中点四等分。转到下节点全局方向后共 16 块，各面积为 A_r/16。此生成方式的几何结果与腿公式之间进行了精确面积核对。
EN: The new program constructs triangles by exact clipping against four exterior half-planes rather than the leg formula, then checks four positive-area triangles and their midpoint quartering. Rotation to the lower node yields 16 pieces of area A_r/16. Their exact areas are reconciled with the leg formula.

ZH: 正面积交叠必使中心位于源矩形减三角形包围盒的开矩形支持域；于是每块积分由其面积乘相关密度和控制。将密度向上取整，精确坐标统一转成无界整数，再对全部事件扫描，得到全局上界而不限制可行中心。
EN: Positive-area intersection requires the center to lie in the open rectangle obtained by subtracting the triangle box from the source rectangle. Each piece's integral is therefore bounded by its area times the relevant density sum. Upward-rounded densities and exactly scaled unbounded integer coordinates permit a complete event sweep over all centers.

ZH: 同坐标事件全部更新后计算下一开条带，零宽条带不取值；纵坐标树叶对应相邻事件开区间。任一边界点处所有含该点的开支持域共同包含一个邻域，因此某个普通单元的非负密度和至少同样大。这样开单元最大值控制所有中心，并允许合法边界接触。
EN: Apply every event at one coordinate before evaluating the next open slab; zero-width slabs are excluded, and vertical leaves represent open intervals between adjacent events. All open supports containing a boundary point contain a common neighborhood, so a generic cell has at least their nonnegative density sum. Thus open-cell maxima bound every center while permitting legal boundary contact.

## ZH: 计数与严格号
## EN: Counting and strictness

ZH: 从各节点阈值及新上界取 chi=min(10001/10000,min_r(tau_r−A_r G_r/16))。所有节点连续覆盖成立时，每个真实 q-parent 的积分至少为 chi；求和对象是原装填中的实际父方块，不是可能重叠的参考方块。
EN: Set chi=min(10001/10000,min_r(tau_r−A_r G_r/16)) using nodal thresholds and fresh bounds. Once all nodal coverage is established, each actual q-parent has integral at least chi. Sum over the actual parents in the original packing, not potentially overlapping reference squares.

ZH: 有限非负矩形密度对面积绝对连续，边界线段质量为零。40 个内部两两不交的父方块总积分至多 M，而 40×99981/100000−3999/100=3/1250>0，得到端点排除。缩放因子 q=L/X 把边长 X 内的单位正方形装填转为 K 内 q 方块装填。
EN: A finite nonnegative rectangle density is absolutely continuous with respect to area, so boundary segments have zero mass. Forty parents with disjoint interiors have total integral at most M, but 40×99981/100000−3999/100=3/1250>0, excluding the endpoint. Scaling by q=L/X transforms unit-square packings at side X into q-square packings in K.

ZH: 7×7 网格提供有限上界。把容器边长限制在 [1,7]、中心限制在 [0,7]^2、角度限制在紧区间 [0,π/2]。顶点包含条件是闭条件；任意两方块的内部不交等价于四组边法向之一存在非严格分离，是有限个闭条件的并。可行集因而紧，容器边长达到最小值。排除 X 后得到 s(40)>X，而非仅 s(40)≥X。
EN: A 7×7 grid supplies a finite upper bound. Restrict container side to [1,7], centers to [0,7]^2, and orientations to the compact interval [0,π/2]. Vertex containment is closed; interior disjointness of each pair is equivalent to non-strict separation along one of their four edge-normal directions, a finite union of closed conditions. The feasible set is compact and the minimum side is attained. Excluding X therefore gives s(40)>X, not merely s(40)≥X.

ZH: 区间运算、编译器、硬件的 IEEE binary64 行为以及所审查的程序仍属于计算证明信任边界；该证明未在形式化证明助理中核验。
EN: Interval arithmetic, compilers, IEEE binary64 hardware behaviour and the reviewed programs remain in the computational-proof trust boundary; this proof has not been checked by a formal proof assistant.
