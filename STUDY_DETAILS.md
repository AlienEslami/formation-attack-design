# Numerical studies and supporting results

## Communication budget

Five aircraft retain the all-pairs physical graph, controller, output scales, and attack scales. The allowed budget is 4 through 10 links. All 315 admissible forward supports are screened. For the steady-state comparison, all supports receive three-start local weight searches. For each dynamic budget and geometry, five supports with the best equal-weight screening scores receive two-start local weight searches. Known designs, the steady-state candidates, and preceding-budget solutions are also retained. The selected design is refined after adding located peak frequencies.

The searches are numerical and local. Neither enumeration of supports nor multiple starts establishes global continuous-weight optimality. The theoretical lower bounds remain distinct from the numerical candidates. All 14 selected budget designs have independent numerical upper bounds over the full frequency range, using the Appendix method. These are padded floating-point evaluations of analytic inequalities, not interval-arithmetic proofs. The largest gap from an attained peak to its numerical upper target is below 0.012.

At the lower geometry, the seven-link candidate has attained gain 9.2902609 and numerical upper bound 9.30. Its follower rows are:

| Receiver | Senders and weights |
| --- | --- |
| 1 | leader: 1 |
| 2 | leader: 0.5217491168; aircraft 1: 0.4782508832 |
| 3 | aircraft 1: 0.3374993263; aircraft 2: 0.6625006737 |
| 4 | leader: 0.4790768487; aircraft 1: 0.5209231513 |

The ten-link candidate has attained gain 9.1096879 and numerical upper bound 9.111, compared with the analytical floor 9.1096879. This establishes near-attainment for that candidate; it does not prove that ten links are necessary for dynamic near-attainment.

Exact weights, all screening and optimization records, and frequency-cover intervals are under `evidence/additional_studies/`.

## Geometry

The lateral increment takes 14 values from 1.0293333333 to 1.35 wingspans, at each of the two height signs. Downstream spacing, height magnitude, local controllers, and communication weights remain fixed. Each point uses a fresh equilibrium and linearization. All 28 points pass the aerodynamic, clearance, separation, and local-stability checks. All ten physical pairs are retained, as are the attack/output scales. The steady-state response is checked at each point.

The three designs are the analytical equal-weight construction, the leader-predecessor design, and the weights adjusted at the original lower geometry. We do not retune weights during the sweep. Figure 5 enlarges the interval where rankings change; all tested larger spacings are retained in `geometry.json`. Plotted geometry gains are refined attained frequency peaks. They are not a guarantee over unsampled geometries or uncertain models.

## Matched-energy nonlinear comparison

Four seven-link designs receive the same attack on link 0 to 1 at the lower geometry. The vertical-position packet corruption is either a bias or a 0.225 rad/s oscillation. It acts from 10 to 100 seconds, has 2-second raised-cosine entry/exit ramps, and is followed by 90 seconds of recovery observation. Each waveform is scaled to normalized input energy 20; the same waveform and amplitude are used for every design. Physical peak amplitudes and actual energies are retained in each JSON record. Velocity and course inputs are uncorrupted.

The reported energy gain is the measured output L2 norm divided by the input L2 norm over this replay. It is a response to a selected waveform, not an estimate of the worst seven-component attack. All eight runs complete within the model domain. The adjusted-weight oscillation is rerun with half the integration step: peak error changes by about 0.003% and the measured energy gain by about 0.0014%.

## Original amplitude tests retained from the previous version

The following tests use the analytical equal-weight design and the original common physical waveforms. The output is maximum pairwise position error divided by peak injected displacement. These tests are preserved in `evidence/original/nonlinear.json` and `evidence/original/nonlinear_cases/`.

| Peak attack / wingspan | Profile | Upper geometry | Lower geometry |
| --- | --- | ---: | ---: |
| 0.00138 | Bias | 0.966 | 1.001 |
| 0.00138 | Oscillation | 0.212 | 1.267 |
| 0.00345 | Bias | Model-domain exit at 50.5 s | 1.001 |
| 0.00345 | Oscillation | 0.212 | Model-domain exit at 44.3 s |

At an exit, a follower's wing reaches the wake model's required clearance from a wake core. No extrapolated response beyond that boundary is reported.

## Reproduction and independent checks

See README.md for the supported public commands. The release includes 117 assembled delayed models: 19 original comparisons, 14 budget designs, and 84 geometry/design combinations. The standalone verifier reconstructs these systems without the aerodynamic code. Aircraft matrices for all 34 operating points are supplied in aircraft_models/ after extraction. Plot reproduction uses the recorded arrays and histories; rerunning the nonlinear aerodynamic simulations requires the original GUAM implementation and model-generation pipeline.

## Complete matched-energy results

| Design | Profile | Peak injected displacement (m) | Peak position error / amplitude | Measured energy gain |
| --- | --- | ---: | ---: | ---: |
| budget_tuned | vertical_bias | 0.01457223 | 1.001506 | 0.540597 |
| constructed | vertical_bias | 0.01457223 | 1.001506 | 0.544308 |
| leader_predecessor | vertical_bias | 0.01457223 | 1.016119 | 0.607102 |
| tuned | vertical_bias | 0.01457223 | 1.001506 | 0.565807 |
| budget_tuned | vertical_oscillation | 0.02054345 | 0.904523 | 0.519019 |
| constructed | vertical_oscillation | 0.02054345 | 1.267283 | 0.809009 |
| leader_predecessor | vertical_oscillation | 0.02054345 | 0.886456 | 0.541127 |
| tuned | vertical_oscillation | 0.02054345 | 0.904395 | 0.637823 |
