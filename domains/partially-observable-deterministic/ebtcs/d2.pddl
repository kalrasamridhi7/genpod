(define (domain btcs)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:types package bomb toilet)

    (:predicates    (in ?p - package ?b - bomb) 
                    (defused ?b - bomb) 
                    (clogged ?t - toilet) 
                    (sensed ?p - package ?b - bomb)
                    (testing)
    )

    (:state-variable (bomb-loc ?b - bomb) (forall (?p - package) (in ?p ?b)))
    (:obs-variable (bomb-in-package ?p - package ?b - bomb) (sensed ?p ?b))         ; binary (sensed) variable

    (:sensing-model
        :parameters (?p - package ?b - bomb)
        :model-for (sensed ?p ?b)
        :precondition (testing)
        :such-that (in ?p ?b)
    )

    (:sensing-model
        :parameters (?p - package ?b - bomb)
        :model-for (not (sensed ?p ?b))
        :precondition (testing)
        :such-that (exists (?q - package) (and (not (= ?q ?p)) (in ?q ?b)))
    )

    (:action test	
        :parameters ()
        :precondition (not (testing))
        :effect (testing)
    )

    (:action dunk	
        :parameters (?p - package ?b - bomb ?t - toilet)
        :precondition (and (not (clogged ?t)) (in ?p ?b))
        :effect (and (defused ?b) (clogged ?t) (not (testing)))
    )

    (:action flush	
        :parameters (?t - toilet)
        :precondition (and (clogged ?t))
        :effect (and (not (clogged ?t)) (not (testing)))
    )
)

