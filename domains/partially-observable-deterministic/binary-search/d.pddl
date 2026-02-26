(define (domain binary-search)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:types state)
    (:predicates 
        (secret ?p - state)
        (lt ?p ?q - state) 
        (less-than ?p - state) 
        (discover-not-yet-attempted) 
        (finish)
        (testing ?p - state)
    )

    (:state-variable (lt-var ?p ?q - state) (lt ?p ?q))            ;binary variable
    (:state-variable (hidden-secret) (forall (?p - state) (secret ?p)))
    (:state-variable (testing-var) (forall (?p - state) (testing ?p)))
    (:obs-variable (obs-test ?p - state) (less-than ?p))           ; binary variable

    (:sensing-model
        :parameters (?p - state)
        :model-for (less-than ?p)
        :precondition (and (testing ?p) (discover-not-yet-attempted))
        :such-that (exists (?q - state) (and (secret ?q) (lt ?q ?p)))
    )

    (:sensing-model
        :parameters (?p - state)
        :model-for (not (less-than ?p))
        :precondition (and (testing ?p) (discover-not-yet-attempted))
        :such-that (or (secret ?p) (exists (?q - state) (and (secret ?q) (lt ?p ?q))))
    )

    (:action test
        :parameters (?p - state)
        :precondition (discover-not-yet-attempted)
        :effect (testing ?p)
    )

    (:action discover	
        :parameters (?p - state)
        :precondition (discover-not-yet-attempted)
        :effect (and (not (discover-not-yet-attempted)) (when (secret ?p) (finish)))
    )
)

