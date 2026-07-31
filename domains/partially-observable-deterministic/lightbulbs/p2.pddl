(define (problem lightbulbs2)
  (:domain lightbulbs)
  (:requirements :strips :typing :existential-preconditions :partial-observability)
  (:objects r11 r12 r21 r22 - room)
  (:init
    (adj r11 r12) (adj r12 r11)
    (adj r11 r21) (adj r21 r11)
    (adj r12 r22) (adj r22 r12)
    (adj r21 r22) (adj r22 r21)

    (need-start)
    (at r11)
    
  )
  (:goal (and (light-on r11) (light-on r12) (light-on r21) (light-on r22)))
)
