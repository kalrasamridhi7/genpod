(define (problem btcs-5-1)
    (:domain btcs)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:objects 
        b0 - bomb
        p0 p1 p2 p3 p4 - package
        t0 - toilet
    )
    (:init (not (clogged t0)) (not (testing)))
    (:goal (defused b0))
)
