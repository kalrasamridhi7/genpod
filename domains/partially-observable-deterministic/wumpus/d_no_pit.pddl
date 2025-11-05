(define (domain wumpus_no_pit)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:types pos)
    (:predicates
        (adj ?p ?q - pos)
        (need-start)
        (at ?p - pos)
        (wumpus-at ?p - pos)
        (gold-at ?p - pos)
        (got-the-treasure)
        (stench ?p - pos)
        (glitter ?p - pos)
        (alive)
    )

    (:sensing-model
        :parameters (?j - pos)
        :model-for (stench ?j)
        :precondition (at ?j)
        :such-that (exists (?p - pos) (and (adj ?j ?p) (wumpus-at ?p)))
    )

    (:sensing-model
        :parameters (?j - pos)
        :model-for (not (stench ?j))
        :precondition (at ?j)
        :such-that (exists (?p - pos) (and (not (adj ?j ?p)) (wumpus-at ?p)))
    )

    (:sensing-model
        :parameters (?j - pos)
        :model-for (not (glitter ?j))
        :precondition (at ?j)
        :such-that (exists (?p - pos) (and (not (= ?p ?j)) (gold-at ?p)))
    )
    
    (:sensing-model
        :parameters (?j - pos)
        :model-for (glitter ?j)
        :precondition (at ?j)
        :such-that (gold-at ?j)
    )

    (:action start
        :parameters (?j - pos)
        :precondition (and (need-start) (alive) (at ?j))
        :effect (not (need-start))
    )

    (:action move
        :parameters (?i ?j - pos)
        :precondition (and (adj ?i ?j) (at ?i) (alive) (not (need-start)) (not (wumpus-at ?j)))
        :effect (and (not (at ?i)) (at ?j)                                      
                     (when (wumpus-at ?j) (not (alive)))                    
                )
    )

    (:action grab
        :parameters (?i - pos)
        :precondition (and (at ?i) (alive) (gold-at ?i) (not (need-start)))
        :effect (and (got-the-treasure) (not (gold-at ?i)))
    )
)