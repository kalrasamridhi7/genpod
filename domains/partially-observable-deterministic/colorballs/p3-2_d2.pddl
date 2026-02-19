(define (problem colorballs-3-1)
    (:domain colorballs)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:objects
        o1 o2 - obj 
        p1-1 p1-2 p1-3
        p2-1 p2-2 p2-3
        p3-1 p3-2 p3-3 - pos
        red blue - col 
        ;t1 t2 - gar 
    )
    (:init
        (adj p1-1 p1-2) (adj p1-2 p1-1)
        (adj p1-1 p2-1) (adj p2-1 p1-1)
        (adj p1-2 p1-3) (adj p1-3 p1-2)
        (adj p1-2 p2-2) (adj p2-2 p1-2)
        (adj p1-3 p2-3) (adj p2-3 p1-3)
        (adj p2-1 p2-2) (adj p2-2 p2-1)
        (adj p2-1 p3-1) (adj p3-1 p2-1)
        (adj p2-2 p2-3) (adj p2-3 p2-2)
        (adj p2-2 p3-2) (adj p3-2 p2-2)
        (adj p2-3 p3-3) (adj p3-3 p2-3)
        (adj p3-1 p3-2) (adj p3-2 p3-1)
        (adj p3-2 p3-3) (adj p3-3 p3-2)

        (garbage-at blue p1-1)
        (garbage-at red p1-3)
        ;(garbage-color t1 red)
        ;(garbage-color t2 blue)

        (at p1-1)
        (need-start)

        (not (trashed o1))
        (not (trashed o2))
        (not (holding o1))
        (not (holding o2))
        (arm-free)

    )
    (:goal (and (trashed o1) (trashed o2)))
)

