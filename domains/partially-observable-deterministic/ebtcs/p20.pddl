(define (problem btcs-20-1)
    (:domain btcs)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:objects 
        b0 - bomb
        p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 - package
        t0 - toilet
    )
    (:init (not (clogged t0)))
    (:goal (defused b0))
)
