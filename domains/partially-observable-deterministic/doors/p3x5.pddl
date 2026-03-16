(define (problem doors3x5)
    (:domain doors)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:objects
        p1-1 p1-2 p1-3
        p2-1 p2-2 p2-3
        p3-1 p3-2 p3-3
        p4-1 p4-2 p4-3
        p5-1 p5-2 p5-3 - pos
        c2 c4 - col
        r1 r2 r3 - row
    )
    (:init
        (adj p1-1 p1-2) (adj p1-2 p1-1)
        (adj p1-1 p2-1)
        (adj p1-2 p1-3) (adj p1-3 p1-2)
        (adj p1-2 p2-2)
        (adj p1-3 p2-3)
        
        (adj p2-1 p2-2) (adj p2-2 p2-1)
        (adj p2-1 p3-1)
        (adj p2-2 p2-3) (adj p2-3 p2-2)
        (adj p2-2 p3-2)
        (adj p2-3 p3-3)
        (adj p3-1 p3-2) (adj p3-2 p3-1)
        (adj p3-1 p4-1)
        (adj p3-2 p3-3) (adj p3-3 p3-2)
        (adj p3-2 p4-2)
        (adj p3-3 p4-3)
        (adj p4-1 p4-2) (adj p4-2 p4-1)
        (adj p4-1 p5-1)
        (adj p4-2 p4-3) (adj p4-3 p4-2)
        (adj p4-2 p5-2)
        (adj p4-3 p5-3)
        (adj p5-1 p5-2) (adj p5-2 p5-1)
        (adj p5-2 p5-3) (adj p5-3 p5-2)

        (at-col c2 p2-1)
        (at-col c2 p2-2)
        (at-col c2 p2-3)
        (at-col c4 p4-1)
        (at-col c4 p4-2)
        (at-col c4 p4-3)

        (at-row r1 p1-1)
        (at-row r1 p2-1)
        (at-row r1 p3-1)
        (at-row r1 p4-1)
        (at-row r1 p5-1)
        (at-row r2 p1-2)
        (at-row r2 p2-2)
        (at-row r2 p3-2)
        (at-row r2 p4-2)
        (at-row r2 p5-2)
        (at-row r3 p1-3)
        (at-row r3 p2-3)
        (at-row r3 p3-3)
        (at-row r3 p4-3)
        (at-row r3 p5-3)

        (right-col c2 p1-1)
        (right-col c2 p1-2)
        (right-col c2 p1-3)
        (right-col c4 p3-1)
        (right-col c4 p3-2)
        (right-col c4 p3-3)

        ;(even c2)
        ;(even c4)

        (need-start)
        (at p1-2)

        (opened p1-1)
        (opened p1-2)
        (opened p1-3)
        (opened p3-1)
        (opened p3-2)
        (opened p3-3)
        (opened p5-1)
        (opened p5-2)
        (opened p5-3)
    )
    (:goal (at p5-3))
)

