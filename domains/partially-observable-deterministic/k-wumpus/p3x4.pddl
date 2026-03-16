(define (problem p3x4)
    (:domain k-wumpus)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:objects
        p1-1 p1-2 p1-3 p1-4
        p2-1 p2-2 p2-3 p2-4
        p3-1 p3-2 p3-3 p3-4 - pos
    )
    (:init
        ; Horizontal adjacencies - Row 1
        (adj p1-1 p1-2) (adj p1-2 p1-1)
        (adj p1-2 p1-3) (adj p1-3 p1-2)
        (adj p1-3 p1-4) (adj p1-4 p1-3)
        
        ; Horizontal adjacencies - Row 2
        (adj p2-1 p2-2) (adj p2-2 p2-1)
        (adj p2-2 p2-3) (adj p2-3 p2-2)
        (adj p2-3 p2-4) (adj p2-4 p2-3)
        
        ; Horizontal adjacencies - Row 3
        (adj p3-1 p3-2) (adj p3-2 p3-1)
        (adj p3-2 p3-3) (adj p3-3 p3-2)
        (adj p3-3 p3-4) (adj p3-4 p3-3)
        
        ; Vertical adjacencies - Column 1
        (adj p1-1 p2-1) (adj p2-1 p1-1)
        (adj p2-1 p3-1) (adj p3-1 p2-1)
        
        ; Vertical adjacencies - Column 2
        (adj p1-2 p2-2) (adj p2-2 p1-2)
        (adj p2-2 p3-2) (adj p3-2 p2-2)
        
        ; Vertical adjacencies - Column 3
        (adj p1-3 p2-3) (adj p2-3 p1-3)
        (adj p2-3 p3-3) (adj p3-3 p2-3)
        
        ; Vertical adjacencies - Column 4
        (adj p1-4 p2-4) (adj p2-4 p1-4)
        (adj p2-4 p3-4) (adj p3-4 p2-4)
        
        (need-start)
        (not (wumpus-at p1-1))
        (not (wumpus-at p2-1))
        (not (wumpus-at p1-2))
        (at p1-1)
        (alive)
        (not (killed))
    )
    (:goal (killed))
)
