# ECC 2027 case-study reproducibility

The additional budget, spacing, and matched-energy studies are documented in `STUDY_DETAILS.md`. The original settings below remain for the earlier comparisons and retained amplitude tests.

## Link-budget checks

The manuscript now includes a general graph budget bound and a corollary for physical trees directed away from the leader. The proofs are in Section III. The script `verify_budget_results.py` supplies independent algebraic and numerical checks; its results are in `evidence/expanded/budget_checks.json`.

For a fixed forward order, the constrained minimum at follower $i$ is $\sigma_i=1/(K_{i:,i:}^{-1})_{11}$, where the trailing principal matrix includes $i$ and all later followers. The script checks this formula exactly for complete graphs of sizes 2 through 8 and minimizes the degree-count relaxation at every budget up to $2N-3$. For the sparse example, it checks all four admissible orders, the six-link lower bound $7/3$, and the attaining seven-link value $15/7$, in units $Q\Gamma_{\mathrm{ss}}^2/\beta^2$. It also checks all forward-oriented rooted trees up to seven vertices and tests the general inequality on sampled physical graphs and communication weights. These checks supplement the proofs; sampling is not used to establish the theorems.

## Steady-state response of the aircraft controller

Let $\eta$ be the weighted sum of the packets received by a follower, with components ordered as $X,Y,Z,V_X,V_Y,V_Z,\chi$. Write $F_{r,c}$ for entry $(r,c)$ of $K_F$, using one-based indices. The cruise reference is fixed. At equilibrium, the position and attitude kinematics give zero velocity and angular-rate deviations. The three pure-integral controller equations require components 1, 2, and 5 of the cooperative command $K_F(\eta-y_i)$ to vanish. Since the equilibrium navigation output is $(X,Y,Z,0,0,0,0)^\top$, those rows give

$$
\begin{aligned}
X &= \eta_X + (F_{1,4}/F_{1,1})\eta_{V_X},\\
Y &= \eta_Y + (F_{5,5}/F_{5,2})\eta_{V_Y} + (F_{5,7}/F_{5,2})\eta_\chi,\\
Z &= \eta_Z + (F_{2,6}/F_{2,3})\eta_{V_Z}.
\end{aligned}
$$

These are the controller equations formerly displayed as equation (25) in the manuscript. The coefficients are evaluated below with positions in feet, velocities in feet per second, and course in radians.

| Coefficient | Value | Unit |
| --- | ---: | --- |
| $F_{1,4}/F_{1,1}$ | 17.27949519496 | s |
| $F_{5,5}/F_{5,2}$ | 0.52418214015 | s |
| $F_{5,7}/F_{5,2}$ | 799.74896474833 | ft/rad |
| $F_{2,6}/F_{2,3}$ | 15.57252927849 | s |

The position outputs depend only on the received packets, so a constant upstream wake input has zero steady-state gain to the navigation output. The map $H_0$ is common because $K_F$ is fixed. It returns a position-only vector and acts as the identity on that subspace, which gives $H_0^2=H_0$. With $S_a=\operatorname{diag}(0.1I_6,0.05\pi/180)$ and $W_F=\operatorname{diag}(I_3/0.095,I_3/2)$, the largest singular value of $W_F[H_0]_{1:6,:}S_a$ is $\beta=18.21937582946$.

The matrix checks in `evidence/original/verification.json` cover every follower and upstream wake link at both geometries for each of the three formation sizes. These stored checks evaluate the local maps at zero frequency and check the three identities from Assumption 1 directly.

## Formation and wake settings

- The lateral increment is `1.0293333333333334` wingspans in the simulation. The paper rounds this to `1.029333`. The downstream increment is `1.5`, the vertical increment is `+0.055` for $q_+$ and `-0.055` for $q_-$, and the wingspan is 14.478 m.
- The convection delay equals nominal downstream separation divided by the 200 ft/s cruise speed. For $N=5,7,9$, the largest delays are 1.425, 2.1375, and 2.85 s, respectively.
- The minimum allowable distance from the follower wing to a wake core is $\max(0.06b,3r_c)$, where $r_c$ is the core radius. The $0.06b$ term governs the reported exits. Both geometries have a minimum nominal clearance margin of approximately $0.00233b$.

## Numerical state-space models

The six files in `aircraft_models/` give the linearizations for both echelons at $N=5,7,9$. Load them with `numpy.load(..., allow_pickle=False)`. Aircraft indices start at zero.

| Array | Definition |
| --- | --- |
| `A_p[i]` | $18\times18$ matrix $A_i^p$, including the local controller and the wake derivatives with respect to the receiver's own state. |
| `B[i]` | $18\times5$ matrix $B_i$ from the cooperative command to the state derivative. |
| `C` | Shared $7\times18$ matrix $C_i$ from the aircraft state to the transmitted output. |
| `P[k]` | $18\times18$ delayed source-state block $P_{ji}$ for the pair $(j,i)$ in `wake_edges[k]`. Its delay in seconds is `delays[k]`. |
| `K_F`, `S_a`, `W_F` | Cooperative gain and attack and output scales used in the paper. |
| `positions_b` | Nominal downstream, lateral, and upward coordinates in wingspans. The state and packet arrays use down-positive vertical position and velocity. |
| `state_order`, `command_order`, `packet_order` | State, cooperative command, and transmitted-output order. |

For each design, `models/` gives the assembled matrices with the leader held on its nominal trajectory. `A` is the instantaneous state matrix, and `delay_matrices[k]` is the state matrix acting at `delays[k]`. `C` maps the states to the scaled pairwise performance output. The seven columns of `B` for each follower contain the attack input matrix for unit link weight. To evaluate an attack on $j\to i$, take the seven columns for follower $i$ and multiply them by the actual weight $w_{ij}$ in `W`. This yields the delayed state-space system used for the full-matrix verification.

## Frequency search and weight tuning

All physical and communication links point forward in the tested formations. At each frequency, we evaluate the followers in order and use the responses of already evaluated upstream aircraft as inputs to the next follower. Each wake term uses the phase factor $e^{-\mathrm{i}\omega\tau_{ji}}$. The search starts with 241 log-spaced frequencies from $10^{-4}$ to $10$ rad/s, zero, extra frequencies near the peaks, and high-frequency points up to $10^4$ rad/s. Local searches refine the attained peaks. Independent delayed state-space solves agree with the ordered calculation to relative error below $10^{-9}$.

For the tuned design, four SLSQP starts minimize the largest sampled gain on the same seven links as the equal-weight design. The search adds refined peak frequencies to the grid. Each leader weight is constrained to $[0.001,0.999]$, and the weight on the other incoming link is its complement. The leader weights for followers 2, 3, and 4 are approximately 0.3864, 0.6902, and 0.6310. The resulting steady-state gain is 9.6202, the attained peak is 10.8638, and its numerical upper bound over all frequencies is 10.87. The search is local. The exact weights and search record are in `evidence/expanded/tuning.json`.

In the five-aircraft wake tests, swapping only the local wake derivatives at $q_-$ for those at $q_+$ lowers the attained peak from 13.9707 to 9.1097. The reverse swap gives an attained peak of 35.5677 at $q_+$. Suppressing the delayed upstream wake terms at $q_-$ also gives an attained peak of 9.1097. All variants have the same steady-state gain. See `evidence/expanded/wake_diagnostics.json` for the frequency and stability checks.

## Nonlinear simulation settings

The attack is applied from 10 to 100 s, with a 2 s raised-cosine ramp at each end and 90 s of observation after removal. The two peak displacement amplitudes are 0.02 and 0.05 m. The integration step is 0.05 s. Halving the step to 0.025 s for the two original time histories preserves completion status and changes individual position histories by less than $3.2\times10^{-8}b$. The check is recorded in `evidence/original/time_step_check.json`.

## Run the checks

From the extracted source and verification package, run `python verify_exported_models.py` with NumPy installed. The script uses the matrices in `models/` to check all 117 exported delayed linear models at six frequencies, including zero. The file `evidence/expanded/equal_budget.json` gives the weights, frequency grid, and attained peak frequency for each receiver. The full-frequency bounds are in `evidence/original/frequency_bounds/` and `evidence/expanded/bounds/`.

The eight nonlinear attack specifications are in `evidence/original/nonlinear_plan.json`. Summaries and time histories are in `evidence/original/nonlinear.json` and `evidence/original/nonlinear_cases/`. Regenerating the nonlinear simulations requires the full project checkout and aerodynamic data. Exact coordinates, operating-point matrices, delays, attack specifications, and recorded histories are included in this release; the full nonlinear model-generation pipeline is not.
