(define (domain binary-search)
    (:types state)
    (:predicates 
        (secret ?p - state)
        (lt ?p ?q - state) 
        (less-than) 
        (discover-not-yet-attempted) 
        (finish)
        (testing ?p)
    )

    (:state-variable (hidden-secret) (forall (?p - state) (secret ?p)))
    (:obs-variable (obs-test) (less-than)) ; binary (sensed) variable

    (:sensing-model
        :parameters (?p - state)
        :model-for (less-than ?p)
        :precondition (testing ?p)
        :such-that (exists (?q - state) (and (secret ?q) (lt ?q ?p)))
    )

    (:sensing-model
        :parameters (?p - state)
        :model-for (not (less-than ?p))
        :precondition (testing ?p)
        :such-that (or (secret ?p) (exists (?q - state) (and (secret ?q) (lt ?p ?q))))
    )

    (:action test
        :parameters (?p - state)
        :effect (testing ?p)
    )

    (:action discover	
        :parameters (?p - state)
        :precondition (discover-not-yet-attempted)
        :effect (and (not (discover-not-yet-attempted)) (when (secret ?p) (finish)))
    )
)

