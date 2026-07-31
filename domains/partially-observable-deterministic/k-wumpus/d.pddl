(define (domain k-wumpus)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:types pos)
    (:predicates
        (adj ?p ?q - pos)
        (need-start)
        (at ?p - pos)
        (wumpus-at ?p - pos)
        (killed)
        (stench ?p - pos)
        (alive)
        (fired)
    )

    (:state-variable (adj-var ?p ?q - pos) (adj ?p ?q))
    (:state-variable (agent-pos) (forall (?p - pos) (at ?p)))                           
    (:state-variable (wumpus-at-var) (forall (?p - pos) (wumpus-at ?p)))
    (:obs-variable (stench-var ?p - pos) (stench ?p))                     ; binary variable
    (:state-variable (killed-var) (killed))
    (:state-variable (fired-var) (fired))

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

    (:action kill
        :parameters (?p1 ?p2 - pos)
        :precondition (and (adj ?p1 ?p2) (at ?p1) (not (fired)) (not (need-start)))
        :effect (and (fired) (when (wumpus-at ?p2) (killed)))
    )
)