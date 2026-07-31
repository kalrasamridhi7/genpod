(define (domain colorballs)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:types pos obj col gar)
    (:predicates
        (adj ?i ?j - pos)
        (color ?o - obj ?c - col)
        (garbage-at ?t - gar ?p - pos)
        (garbage-color ?t - gar ?c - col)
        (trashed ?o - obj)
        (at ?i - pos)
        (holding ?o - obj)
        (obj-at ?o - obj ?i - pos)
        (obs-obj-at ?o - obj ?i - pos)
        (obs-obj-col ?o - obj ?c -col)
        (need-start)
        (arm-free)
    )

    (:state-variable (adj-var ?p ?q - pos) (adj ?p ?q))
    (:state-variable (garbage-at-var ?t - gar ?p - pos) (garbage-at ?t ?p))
    (:state-variable (garbage-color-var ?t - gar ?c - col) (garbage-color ?t ?c))
    (:state-variable (trashed-var ?o - obj) (trashed ?o))
    (:state-variable (holding-var ?o - obj) (holding ?o))
    (:state-variable (var-agent-at) (forall (?p - pos) (at ?p)))                          
    (:state-variable (var-obj-at ?o - obj) (or (holding ?o) (trashed ?o)) (forall (?p - pos) (obj-at ?o ?p)))
    (:state-variable (var-obj-col ?o - obj) (forall (?c - col) (color ?o ?c)))
    (:obs-variable (var-obs-at ?o - obj ?p - pos) (obs-obj-at ?o ?p)) ; binary
    (:obs-variable (var-obs-col ?o - obj) (forall (?c - col) (obs-obj-col ?o ?c)))

    (:sensing-model
        :parameters (?o - obj ?p - pos)
        :model-for (obs-obj-at ?o ?p)
        :precondition (and (at ?p) (not (need-start)))
        :such-that (obj-at ?o ?p)
    )

    (:sensing-model
        :parameters (?o - obj ?p - pos)
        :model-for (not (obs-obj-at ?o ?p))
        :precondition (and (at ?p) (not (need-start)))
        :such-that (not (obj-at ?o ?p))
    )

    (:sensing-model
        :parameters (?o - obj ?c - col)
        :model-for (obs-obj-col ?o ?c)
        :precondition (and (holding ?o) (not (need-start)))
        :such-that (color ?o ?c)
    )
    
    (:action start-action
        :parameters (?p - pos)
        :precondition (and (at ?p) (need-start))
        :effect (not (need-start))
    )

    (:action move
        :parameters (?i ?j - pos)
        :precondition (and (adj ?i ?j) (at ?i) (not (need-start)) )
        :effect (and (not (at ?i)) (at ?j))
    )

    (:action pickup
        :parameters (?o - obj ?i - pos)
        :precondition (and (at ?i) (obj-at ?o ?i) (not (need-start)) (arm-free))
        :effect (and (holding ?o) (not (obj-at ?o ?i)) (not (arm-free)))
    )
    
    (:action trash
        :parameters (?o - obj ?c - col ?t - gar ?p - pos)
        :precondition (and (holding ?o) (at ?p) (garbage-at ?t ?p) (color ?o ?c) (garbage-color ?t ?c))
        :effect (and (trashed ?o) (not (holding ?o)) (arm-free))
    )
)

