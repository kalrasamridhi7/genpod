(define (domain lightbulbs)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:types room)
    (:predicates
        (adj ?p ?q - room)
        (need-start)
        (at ?p - room)
        (bright ?p - room)
        (light-on ?p - room)
    )

    (:state-variable (adj-var ?p ?q - room) (adj ?p ?q))
    (:state-variable (agent-room) (forall (?p - room) (at ?p)))                           
    ;(:state-variable (light-on-var ?p - room) (light-on ?p))
    (:obs-variable (bright-var ?p - room) (bright ?p))

    (:sensing-model
        :parameters (?j - room)
        :model-for (not (bright ?j))
        :precondition (at ?j)
        :such-that (not (light-on ?j))
    )
    
    (:sensing-model
        :parameters (?j - room)
        :model-for (bright ?j)
        :precondition (at ?j)
        :such-that (light-on ?j)
    )

    (:action start
        :parameters (?j - room)
        :precondition (and (need-start) (at ?j))
        :effect (not (need-start))
    )

    (:action move
        :parameters (?i ?j - room)
        :precondition (and (adj ?i ?j) (at ?i) (not (need-start)))
        :effect (and (not (at ?i)) (at ?j))
    )

    (:action toggle-on
        :parameters (?p - room)
        :precondition (and (at ?p) (not (need-start)) (not (light-on ?p)))
        :effect (light-on ?p)
    )
)