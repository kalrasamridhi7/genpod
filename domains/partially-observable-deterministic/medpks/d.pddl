(define (domain medical)
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:types ILLNESS)
    (:predicates 
        (dead) (cured) (testing)
        ;(no-stain) 
        (stain ?i - ILLNESS) 
        (ill ?i - ILLNESS)    
    )

    (:state-variable (alive) (dead))
    (:state-variable (disease) (cured) (forall (?i - ILLNESS) (ill ?i)))
    ;(:obs-variable (test-result) (no-stain) (forall (?i - ILLNESS) (stain ?i)))
    (:obs-variable (test-result) (no-stain) (forall (?i - ILLNESS) (stain ?i)))

    ;(:sensing-model
    ;    :parameters ()
    ;    :model-for (no-stain)
    ;    :precondition (testing)
    ;    :such-that (cured)
    ;)

    (:sensing-model
        :parameters (?i - ILLNESS)
        :model-for (stain ?i)
        :precondition (testing)
        :such-that (ill ?i)
    )

    (:action medicate-for
        :parameters (?i - ILLNESS)
        :precondition (not (dead))
        :effect
            (and
                (forall (?j - ILLNESS)
                     (when (and (ill ?j) (= ?i ?j)) (and (cured) (not (ill ?j))))
                 )
                 (forall (?j - ILLNESS)
                          (when (and (ill ?j) (not (= ?i ?j))) (dead))
                 )
            )
    )

    (:action do-test
        :parameters ()
        :precondition (not (testing))
        :effect (testing)
    )
)

