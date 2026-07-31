(define (problem lightbulbs5)
  (:domain lightbulbs)
  (:requirements :strips :typing :existential-preconditions :partial-observability)
  (:objects
    r11 r12 r13
    r21 r22 r23
    r31 r32 r33 - room
  )
  (:init
    (adj r11 r12) (adj r12 r11)
    (adj r12 r13) (adj r13 r12)
    (adj r21 r22) (adj r22 r21)
    (adj r22 r23) (adj r23 r22)
    (adj r31 r32) (adj r32 r31)
    (adj r32 r33) (adj r33 r32)

    (adj r11 r21) (adj r21 r11)
    (adj r12 r22) (adj r22 r12)
    (adj r13 r23) (adj r23 r13)
    (adj r21 r31) (adj r31 r21)
    (adj r22 r32) (adj r32 r22)
    (adj r23 r33) (adj r33 r23)

    (need-start)
    (at r11)
    
  )
  (:goal (and (light-on r11) (light-on r12) (light-on r13)
              (light-on r21) (light-on r22) (light-on r23)
              (light-on r31) (light-on r32) (light-on r33)))
)
