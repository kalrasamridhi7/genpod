(define (problem colorballs-5-1)
    (:domain colorballs)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:objects
        o1 - obj 
        p1-1 p1-2 p1-3 p1-4 p1-5
        p2-1 p2-2 p2-3 p2-4 p2-5
        p3-1 p3-2 p3-3 p3-4 p3-5
        p4-1 p4-2 p4-3 p4-4 p4-5
        p5-1 p5-2 p5-3 p5-4 p5-5 - pos 
        red blue - col 
        t1 t2 - gar 
    )
    (:init
        (adj p1-1 p1-2) (adj p1-2 p1-1)
        (adj p1-1 p2-1) (adj p2-1 p1-1)
        (adj p1-2 p1-3) (adj p1-3 p1-2)
        (adj p1-2 p2-2) (adj p2-2 p1-2)
        (adj p1-3 p1-4) (adj p1-4 p1-3)
        (adj p1-3 p2-3) (adj p2-3 p1-3)
        (adj p1-4 p1-5) (adj p1-5 p1-4)
        (adj p1-4 p2-4) (adj p2-4 p1-4)
        (adj p1-5 p2-5) (adj p2-5 p1-5)

        (adj p2-1 p2-2) (adj p2-2 p2-1)
        (adj p2-1 p3-1) (adj p3-1 p2-1)
        (adj p2-2 p2-3) (adj p2-3 p2-2)
        (adj p2-2 p3-2) (adj p3-2 p2-2)
        (adj p2-3 p2-4) (adj p2-4 p2-3)
        (adj p2-3 p3-3) (adj p3-3 p2-3)
        (adj p2-4 p2-5) (adj p2-5 p2-4)
        (adj p2-4 p3-4) (adj p3-4 p2-4)
        (adj p2-5 p3-5) (adj p3-5 p2-5)

        (adj p3-1 p3-2) (adj p3-2 p3-1)
        (adj p3-1 p4-1) (adj p4-1 p3-1)
        (adj p3-2 p3-3) (adj p3-3 p3-2)
        (adj p3-2 p4-2) (adj p4-2 p3-2)
        (adj p3-3 p3-4) (adj p3-4 p3-3)
        (adj p3-3 p4-3) (adj p4-3 p3-3)
        (adj p3-4 p3-5) (adj p3-5 p3-4)
        (adj p3-4 p4-4) (adj p4-4 p3-4)
        (adj p3-5 p4-5) (adj p4-5 p3-5)

        (adj p4-1 p4-2) (adj p4-2 p4-1)
        (adj p4-1 p5-1) (adj p5-1 p4-1)
        (adj p4-2 p4-3) (adj p4-3 p4-2)
        (adj p4-2 p5-2) (adj p5-2 p4-2)
        (adj p4-3 p4-4) (adj p4-4 p4-3)
        (adj p4-3 p5-3) (adj p5-3 p4-3)
        (adj p4-4 p4-5) (adj p4-5 p4-4)
        (adj p4-4 p5-4) (adj p5-4 p4-4)
        (adj p4-5 p5-5) (adj p5-5 p4-5)

        (adj p5-1 p5-2) (adj p5-2 p5-1)
        (adj p5-2 p5-3) (adj p5-3 p5-2)
        (adj p5-3 p5-4) (adj p5-4 p5-3)
        (adj p5-4 p5-5) (adj p5-5 p5-4)

        (garbage-at t1 p1-1)
        (garbage-at t2 p1-5)
        (garbage-color t1 red)
        (garbage-color t2 blue)

        (at p1-2)
        (need-start)

        (not (trashed o1))
        (not (holding o1))
        (arm-free)

    )
    (:goal (and (trashed o1)))
)
