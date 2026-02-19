(define (domain doors) 
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:types row col pos)
    (:predicates
        (adj ?i ?j - pos)              ; (static) vertical and right-horizontal adjacency of positions
        (at-col ?c - col ?i - pos)     ; (static) column for given position
        (at-row ?r - row ?i - pos)     ; (static) row for given position
        (right-col ?c - col ?i - pos)  ; (static) column to the right of given position
        ;(even ?c - col)                ; (static) even-numbered columns
        (need-start)
        (at ?i - pos)                  ; current position
        (opened ?i - pos)              ; hidden and static
        (obs-open ?i - pos)            ; observable
    )

    (:state-variable (adj-var ?i ?j - pos) (adj ?i ?j))                     ; binary variable
    (:state-variable (at-col-var ?c - col ?i - pos) (at-col ?c ?i))         ; binary variable
    (:state-variable (at-row-var ?r - row ?i - pos) (at-row ?r ?i))         ; binary variable
    (:state-variable (right-col ?c - col ?i - pos) (right-col ?c ?i))       ; binary variable

    (:state-variable (agent-pos) (forall (?i - pos) (at ?i)))
    ;(:state-variable (door-at ?c - col) such-that (even ?c) (forall (?i - pos) (when (at-col ?c ?i) (opened ?i))))
    (:obs-variable (obs-at ?i - pos) (obs-open ?i))                         ; binary variable

    (:sensing-model
        :parameters (?i - pos)
        :model-for (obs-open ?i)
        :precondition (at ?i)
        :such-that (exists (?p - pos ?c - col ?r - row) (and (at-row ?r ?i) 
                                                            (at-row ?r ?p) 
                                                            (right-col ?c ?i) 
                                                            (at-col ?c ?p)
                                                            (opened ?p)))
    )

    (:sensing-model
        :parameters (?i - pos)
        :model-for (not (obs-open ?i))
        :precondition (at ?i)
        :such-that (exists (?p - pos ?c - col ?r - row) (and (at-row ?r ?i) 
                                                            (at-row ?r ?p) 
                                                            (right-col ?c ?i) 
                                                            (at-col ?c ?p)
                                                            (not (opened ?p))))
    )
                
    (:action start
        :parameters (?i - pos)
        :precondition (and (at ?i) (need-start))
        :effect (not (need-start))
    )

    (:action move
        :parameters (?i - pos ?j - pos)
        :precondition (and (adj ?i ?j) (at ?i) (opened ?j) (not (need-start)))
        :effect (and (not (at ?i)) (at ?j)) 
    )
)

