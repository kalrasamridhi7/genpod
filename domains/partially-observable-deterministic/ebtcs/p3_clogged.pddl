(define (problem btcs-3-1-clogged)
    (:domain btcs)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:objects 
        b0 - bomb
        p0 p1 p2 - package
        t0 - toilet
    )
    (:init (clogged t0)
            (not (testing))
    )
    (:goal (defused b0))
)
