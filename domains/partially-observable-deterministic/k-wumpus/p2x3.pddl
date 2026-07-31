(define (problem p2x3)
    (:domain wumpus)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:objects
        p1-1 p1-2
        p2-1 p2-2
        p3-1 p3-2 - pos
    )
    (:init
        (adj p1-1 p1-2) (adj p1-2 p1-1)
        (adj p1-1 p2-1) (adj p2-1 p1-1)
        (adj p1-2 p2-2) (adj p2-2 p1-2)
        
        (adj p2-1 p2-2) (adj p2-2 p2-1)
        (adj p2-1 p3-1) (adj p3-1 p2-1)
        (adj p2-2 p3-2) (adj p3-2 p2-2)
        
        (adj p3-1 p3-2) (adj p3-2 p3-1)
        
        (need-start)
        (not (wumpus-at p1-1))
        (not (wumpus-at p1-2))
        (not (wumpus-at p2-1))
        (at p1-1)
        (alive)
        (not (fired))
        (not (killed))
    )
    (:goal (killed))
)
