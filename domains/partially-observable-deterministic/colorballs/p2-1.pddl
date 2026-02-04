(define (problem colorballs-2-1)
    (:domain colorballs)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:objects
        o1 - obj 
        p1-1 p1-2
        p2-1 p2-2 - pos 
        red blue - col 
        t2 - gar 
    )
    (:init
        (adj p1-1 p1-2) (adj p1-2 p1-1)
        (adj p1-1 p2-1) (adj p2-1 p1-1)
        (adj p1-2 p2-2) (adj p2-2 p1-2)
        (adj p2-1 p2-2) (adj p2-2 p2-1)

        ;(garbage-at t1 p1-1)
        (garbage-at t2 p2-2)
        ;(garbage-color t1 red)
        ;(garbage-color t2 blue)
        (garbage-color t2 red)

        (at p1-1)
        (need-start)

        (not (trashed o1))
        (not (holding o1))
        (not (trashed o2))
        (not (holding o2))
        (not (stuck))

    )
    (:goal (and (trashed o1)))
)

