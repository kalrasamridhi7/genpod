(define (domain localize) 
    (:requirements :strips :typing :existential-preconditions :partial-observability)
    (:types pos)
    (:predicates
        (wall-up-of ?i - pos)    ; static predicate
        (wall-right-of ?i - pos) ; static predicate
        (wall-down-of ?i - pos)  ; static predicate
        (wall-left-of ?i - pos)  ; static predicate
        (up-of ?i ?j - pos)      ; static predicate
        (right-of ?i ?j - pos)   ; static predicate
        (down-of ?i ?j - pos)    ; static predicate
        (left-of ?i ?j - pos)    ; static predicate
        (possible ?i - pos)      ; static predicate

        (at ?i - pos)

        (free-up)
        (free-down)
        (free-left)
        (free-right)

        (need-start)
    )
    
    (:state-variable (wall-up-of-var ?i - pos) (wall-up-of ?i))         ;binary variable
    (:state-variable (wall-right-of-var ?i - pos) (wall-right-of ?i))   ;binary variable
    (:state-variable (wall-down-of-var ?i - pos) (wall-down-of ?i))     ;binary variable
    (:state-variable (wall-left-of-var ?i - pos) (wall-left-of ?i))     ;binary variable

    (:state-variable (up-of-var ?i ?j - pos) (up-of ?i ?j))               ;binary variable
    (:state-variable (right-of-var ?i ?j - pos) (right-of ?i ?j))         ;binary variable
    (:state-variable (down-of-var ?i ?j - pos) (down-of ?i ?j))           ;binary variable
    (:state-variable (left-of-var ?i ?j - pos) (left-of ?i ?j))      ;binary variable
    
    (:state-variable (possible-var ?i - pos) (possible ?i))       ;binary variable

    (:state-variable (position) (not (possible ?i)) (forall (?i - pos) (at ?i)))
    (:obs-variable (obs-up) (free-up))         ; binary variable
    (:obs-variable (obs-right) (free-right))   ; binary variable
    (:obs-variable (obs-down) (free-down))     ; binary variable
    (:obs-variable (obs-left) (free-left))     ; binary variable

    (:sensing-model
        :parameters ()
        :model-for (free-up)
        :precondition (not (need-start))
        :such-that (exists (?i - pos) (and (at ?i) (possible ?i) (not (wall-up-of ?i))))
    )

    (:sensing-model
        :parameters ()
        :model-for (not (free-up))
        :precondition (not (need-start))
        :such-that (exists (?i - pos) (and (at ?i) (possible ?i) (wall-up-of ?i)))
    )

    (:sensing-model
        :parameters ()
        :model-for (free-right)
        :precondition (not (need-start))
        :such-that (exists (?i - pos) (and (at ?i) (possible ?i) (not (wall-right-of ?i))))
    )

    (:sensing-model
        :parameters ()
        :model-for (not (free-right))
        :precondition (not (need-start))
        :such-that (exists (?i - pos) (and (at ?i) (possible ?i) (wall-right-of ?i)))
    )

    (:sensing-model
        :parameters ()
        :model-for (free-down)
        :precondition (not (need-start))
        :such-that (exists (?i - pos) (and (at ?i) (possible ?i) (not (wall-down-of ?i))))
    )

    (:sensing-model
        :parameters ()
        :model-for (not (free-down))
        :precondition (not (need-start))
        :such-that (exists (?i - pos) (and (at ?i) (possible ?i) (wall-down-of ?i)))
    )

    (:sensing-model
        :parameters ()
        :model-for (free-left)
        :precondition (not (need-start))
        :such-that (exists (?i - pos) (and (at ?i) (possible ?i) (not (wall-left-of ?i))))
    )

    (:sensing-model
        :parameters ()
        :model-for (not (free-left))
        :precondition (not (need-start))
        :such-that (exists (?i - pos) (and (at ?i) (possible ?i) (wall-left-of ?i)))
    )

    (:action start
        :parameters ()
        :precondition (need-start)
        :effect (not (need-start))
    )

    (:action move-up
        :parameters ()
        :precondition (not (need-start))
        :effect (and (forall (?j - pos ?i - pos) (when (and (up-of ?i ?j) (at ?i) (possible ?j)) (and (at ?j) (not (at ?i))))))
    )

    (:action move-down
        :parameters ()
        :precondition (not (need-start))
        :effect (and (forall (?j - pos ?i - pos) (when (and (down-of ?i ?j) (at ?i) (possible ?j)) (and (at ?j) (not (at ?i))))))
    )

    (:action move-left
        :parameters ()
        :precondition (not (need-start))
        :effect (and (forall (?j - pos ?i - pos) (when (and (left-of ?i ?j) (at ?i) (possible ?j)) (and (at ?j) (not (at ?i))))))
    )

    (:action move-right
        :parameters ()
        :precondition (not (need-start))
        :effect (and (forall (?j - pos ?i - pos) (when (and (right-of ?i ?j) (at ?i) (possible ?j)) (and (at ?j) (not (at ?i))))))
    )
)

