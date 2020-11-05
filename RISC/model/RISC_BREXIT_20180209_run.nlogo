extensions [ table gis profiler csv vid]
globals
[
  year-start
  year-end
  year
  p-beef-list
  p-dairy-list
  p-hay-list
  p-straw-list
  cutoff-large-medium
  cutoff-medium-small
  barley-to-straw ;; hectare to tonnes
  oats-to-straw
  grass-to-feed
  roughGrazing-to-feed
  cattle-to-straw-beef ;; tonnes per cattle
  cattle-to-grass-beef
  cattle-to-straw-dairy
  cattle-to-grass-dairy
  ;; assume the number of beef cattle can expand/shrink faster than the number of dairy cattle
  max-rate-expand-beef
  max-rate-shrink-beef
  max-rate-expand-dairy
  max-rate-shrink-dairy
  max-rate-shrink-quit-no-succession
  n-cattle-list-beef
  n-cattle-list-dairy
  n-calf-list-beef
  n-calf-list-dairy
  n-breeder-list-beef
  n-breeder-list-dairy
  n-service-bull-list
  n-cattle-list-other
  n-cattle-list-all
  annual-yield-per-cow-list
;  p-large-group-institution
  year-brexit
  p-beef
  p-dairy
  p-hay
  p-straw
  annual-yield-per-cow
  last-year-holding-data
  expand-buffer
  shrink-buffer
  actual-vertical-distance ;; in km
  km-per-patch
  result-list-farm
  result-list-cattle
]

breed [holdings holding]
holdings-own
[
  holding-code
  holding-patch
  cattle-beef
  cattle-dairy
  calf-beef
  calf-dairy
  breeder-beef
  breeder-dairy
  service-bull
  cattle-other
  cattle-all
  initial-cattle-beef
  initial-cattle-dairy
  initial-calf-beef
  initial-calf-dairy
  initial-breeder-beef
  initial-breeder-dairy
  initial-service-bull
  initial-cattle-other
  initial-cattle-all
  area-barley ;; item 16+18
  area-oats;; item 17+20
  area-grass
  area-roughGrazing ;; item47
  area-total ;; item50
  own-feed-straw
  own-feed-grass
  profit-list-beef
  profit-list-dairy
  group ;; level 0 clustering, large(1), medium(2), small(3)
  initial-group
  off-farm-income-list
  successor-list
  off-farm-income?
  successor?
  manager?
  tourism?
  initial-manager?
  initial-tourism?
  area
  profit-driven?
  leisure-driven?
  tourism-driven?
  ready-to-quit?
]

breed [decisions decision]
decisions-own
[
  decision-maker
  decision-object
  action
]

patches-own
[
  six-fold
  lfa ;; least favoured area, 0 outside, 1 less distadvantaged; 2 severely disadvantaged
  region-name ;; aberdeen
  country-name ;; england scotland
]

breed [centroids centroid]

breed [region-labels region-label]
region-labels-own
[
  region-label-name
]

to setup
  clear-all
  setup-globals
  show "setup-holdings..."
  setup-holdings
  show "setup-holding-geography..."
  setup-holding-geography
  setup-urban-rural
  setup-country-region
  setup-less-favoured-area
  setup-patch-color
  read-off-farm
  read-successor
  read-manager
  read-tourism
  read-size
  update-total-size-cattle
  update-total-size-calf
  update-total-size-breeder
  update-total-size-service-bull
  update-total-size-other
  update-total-size-all
  reset-ticks
  update-price
  ask holdings
  [
    update-off-farm-income
    update-succession
  ]
end

to go
  update-price
  if succession-issue?
  [
    ask holdings
    [
      update-succession
    ]
  ]
  if leisure-farm?
  [
    ask holdings
    [
      update-off-farm-income
    ]
  ]
  if diversification?
  [
    ask holdings
    [
      update-tourism
    ]
  ]
  ask holdings
  [
    update-motivation
  ]
  if industrialization?
  [
    ask holdings
    [
      update-manager
    ]
  ]
  ;; cattle
  ask holdings with [ready-to-quit?]
  [
    update-decision-quit
  ]
  ask holdings with [profit-driven?]
  [
    update-profit-list
    update-decision-profit-cattle
  ]
  ask decisions with [decision-object = "cattle-beef" or decision-object = "cattle-dairy"]
  [
    implement-decision
  ]
  update-total-size-cattle
  ;; calf
  ask holdings with [profit-driven?]
  [
    update-decision-profit-calf
  ]
  ask decisions with [decision-object = "calf-beef" or decision-object = "calf-dairy"]
  [
    implement-decision
  ]
  update-total-size-calf
  ;; breeder
  ask holdings with [profit-driven?]
  [
    update-decision-profit-breeder
  ]
  ask decisions with [decision-object = "breeder-beef" or decision-object = "breeder-dairy"]
  [
    implement-decision
  ]
  update-total-size-breeder
  ;; service bull
  ask holdings with [profit-driven?]
  [
    update-decision-profit-service-bull
  ]
  ask decisions with [decision-object = "service-bull"]
  [
    implement-decision
  ]
  update-total-size-service-bull
  ;; other
  ask holdings with [profit-driven?]
  [
    update-decision-profit-other
  ]
  ask decisions with [decision-object = "cattle-other"]
  [
    implement-decision
  ]
  update-total-size-other
  ask holdings
  [
    update-size-group
  ]
  update-total-size-all
  update-holding-shape-size
  write-result-to-list
  ask decisions
  [
    die
  ]
  set year year + 1
  tick
end

to write-result-to-list
  set result-list-farm lput (list year count holdings with [group = 3] count holdings with [group = 2] count holdings with [group = 1]) result-list-farm
  set result-list-cattle lput (list year sum [cattle-all] of holdings sum [cattle-beef + calf-beef + breeder-beef] of holdings sum [cattle-dairy + calf-dairy + breeder-dairy] of holdings) result-list-cattle
end

to run-all-scenarios-n-times
  let j 1
  foreach (list "S0 no brexit" "S1 FTA" "S2 WTO" "S3 UTL")
  [
    [this-scenario]->
    foreach (list TRUE FALSE)
    [
      [this-succession-issue?]->
      foreach (list TRUE FALSE)
      [
        [this-leisure-farm?]->
        foreach (list TRUE FALSE)
        [
          [this-diversification?]->
          foreach (list TRUE FALSE)
          [
            [this-industrialization?]->
            let i 1
            while [i <= n-runs]
            [
              set scenario this-scenario
              set succession-issue? this-succession-issue?
              set leisure-farm? this-leisure-farm?
              set diversification? this-diversification?
              set industrialization? this-industrialization?
              run-till-2030
              let exp-name (word scenario "-" succession-issue? "-" leisure-farm? "-" diversification? "-" industrialization?)
              let file-farm (word "results/farm-" exp-name "-" i ".csv")
              let file-cattle (word "results/cattle-" exp-name "-" i ".csv")
              csv:to-file file-farm result-list-farm
              csv:to-file file-cattle result-list-cattle
              show (word i ": " exp-name " ; " j)
              set i i + 1
              set j j + 1
            ]
          ]
        ]
      ]
    ]
  ]
end

;; holding procedure, which motivation dominates??
to update-motivation
  set profit-driven? false
  set leisure-driven? false
  set tourism-driven? false
  set ready-to-quit? false
  if leisure-farm? and off-farm-income?
  [
    set leisure-driven? true
  ]
  if diversification? and tourism?
  [
    set tourism-driven? true
  ]
  if not leisure-driven? and not tourism-driven? and succession-issue? and not successor?
  [
    set ready-to-quit? true
  ]
  if not leisure-driven? and not tourism-driven? and not ready-to-quit?
  [
    set profit-driven? true
  ]
end

to make-video
  reset
  vid:start-recorder
  vid:record-view
  repeat 31
  [
    go
    repeat 10
    [
      vid:record-view
    ]
  ]
  vid:save-recording "video_risc.mp4"
end

to run-till-2030
  reset
  repeat 31
  [
    go
  ]
end

to setup-globals
  set year-start 2000
  set year-end 2025
  set year year-start
  set cutoff-large-medium 368 ;; (356+380)/2
  set cutoff-medium-small 131 ;; (124+138)/2
  set p-beef-list []
  set p-dairy-list []
  set p-hay-list []
  set p-straw-list []
  set annual-yield-per-cow-list [] ;; liter
  read-price
  set barley-to-straw 0.1 ;; hectare to tonnes
  set oats-to-straw 0.1 ;; hectare to tonnes
  set grass-to-feed 1 ;; hectare to tonnes
  set roughGrazing-to-feed 0.1 ;; hectare to tonnes
  set cattle-to-straw-beef 0.01 ;; in tonnes
  set cattle-to-straw-dairy 0.02 ;; in tonnes
  set cattle-to-grass-beef 0.1 ;; in tonnes
  set cattle-to-grass-dairy 0.2 ;; in tonnes
  set max-rate-expand-beef 0.1
  set max-rate-shrink-beef 0.1
  set max-rate-expand-dairy 0.1
  set max-rate-shrink-dairy 0.1
  set max-rate-shrink-quit-no-succession 0.2
  set n-cattle-list-beef []
  set n-cattle-list-dairy []
  set n-calf-list-beef []
  set n-calf-list-dairy []
  set n-breeder-list-beef []
  set n-breeder-list-dairy []
  set n-service-bull-list []
  set n-cattle-list-other []
  set n-cattle-list-all []
  set year-brexit 2019
  set last-year-holding-data 2012
  set expand-buffer 0.05
  set shrink-buffer 0.05
  set actual-vertical-distance 682 ;; km
  set km-per-patch actual-vertical-distance / max-pycor
  set result-list-farm (list (list "year" "n small" "n medium" "n large"))
  set result-list-cattle (list (list "year" "n cattle" "n beef" "n dairy"))
end

to setup-holdings
  let dta csv:from-file "dataSSC/dta_initialization.csv"
  let headings first dta
  set dta but-first dta
  while [not empty? dta]
  [
    let data-line first dta
    set dta but-first dta
    create-holdings 1
    [
      (foreach headings data-line
        [
          [this-heading value ] ->
          if this-heading = "HOLDING_CODE"
          [
            set holding-code value
          ]
          if this-heading = "cattle_beef"
          [
            set cattle-beef value
          ]
          if this-heading = "cattle_dairy"
          [
            set cattle-dairy value
          ]
          if this-heading = "calf_beef"
          [
            set calf-beef value
          ]
          if this-heading = "calf_dairy"
          [
            set calf-dairy value
          ]
          if this-heading = "service_bull"
          [
            set service-bull value
          ]
          if this-heading = "breeder_beef"
          [
            set breeder-beef value
          ]
          if this-heading = "breeder_dairy"
          [
            set breeder-dairy value
          ]
          if this-heading = "cattle_other"
          [
            set cattle-other value
          ]
          if this-heading = "barley"
          [
            set area-barley value
          ]
          if this-heading = "oats"
          [
            set area-oats value
          ]
          if this-heading = "grass"
          [
            set area-grass value
          ]
          if this-heading = "roughGraz"
          [
            set area-roughGrazing value
          ]
          if this-heading = "area"
          [
            set area-total value
          ]
          update-size-group
          set own-feed-straw barley-to-straw * area-barley + oats-to-straw * area-oats
          set own-feed-grass grass-to-feed * area-grass + roughGrazing-to-feed * area-roughGrazing
          set profit-list-beef []
          set profit-list-dairy []
          update-profit-list
          set initial-cattle-beef cattle-beef
          set initial-cattle-dairy cattle-dairy
          set initial-calf-beef calf-beef
          set initial-calf-dairy calf-dairy
          set initial-breeder-beef breeder-beef
          set initial-breeder-dairy breeder-dairy
          set initial-service-bull service-bull
          set initial-cattle-other cattle-other
          set initial-cattle-all cattle-all
          set initial-group group
        ]
      )
     ]
  ]
  show word "number of holdings: " count holdings
end

to reset
  clear-all-plots
  setup-globals
  ask holdings
  [
    set cattle-beef initial-cattle-beef
    set cattle-dairy initial-cattle-dairy
    set calf-beef initial-calf-beef
    set calf-dairy initial-calf-dairy
    set breeder-beef initial-breeder-beef
    set breeder-dairy initial-breeder-dairy
    set service-bull initial-service-bull
    set cattle-other initial-cattle-other
    set cattle-all initial-cattle-all
    set group initial-group
;    set own-feed-straw barley-to-straw * area-barley + oats-to-straw * area-oats
;    set own-feed-grass grass-to-feed * area-grass + roughGrazing-to-feed * area-roughGrazing
    set profit-list-beef []
    set profit-list-dairy []
    update-profit-list
    set off-farm-income? item 0 off-farm-income-list
    set successor? item 0 successor-list
    set tourism? initial-tourism?
    set manager? initial-manager?
  ]
  update-total-size-cattle
  update-total-size-calf
  update-total-size-breeder
  update-total-size-service-bull
  update-total-size-other
  update-total-size-all
  update-holding-shape-size
  reset-ticks
end

to read-off-farm
  show "read-off-farm..."
  file-open "dataSSC/off-farm.csv"
  let var-names csv:from-row file-read-line
  show var-names
  while [not file-at-end? ]
  [
    let row csv:from-row file-read-line
    let this-holding-code first row
    let this-holding one-of holdings with [holding-code = this-holding-code]
    if this-holding != nobody
    [
      ask this-holding
      [
        set off-farm-income-list but-first row
      ]
    ]
  ]
  file-close
end

to read-successor
  show "read-successor..."
  file-open "dataSSC/successor.csv"
  let var-names csv:from-row file-read-line
  show var-names
  while [not file-at-end? ]
  [
    let row csv:from-row file-read-line
    let this-holding-code first row
    let this-holding one-of holdings with [holding-code = this-holding-code]
    if this-holding != nobody
    [
      ask this-holding
      [
        set successor-list but-first row
      ]
    ]
  ]
  file-close
end

;; holding procedure
to update-profit-list
  ifelse cattle-beef > 0
  [
    let profit-beef calculate-profit-beef
    set profit-list-beef lput profit-beef profit-list-beef
  ]
  [
    set profit-list-beef lput 0 profit-list-beef
  ]
  ifelse cattle-dairy > 0
  [
    let profit-dairy calculate-profit-dairy
    set profit-list-dairy lput profit-dairy profit-list-dairy
  ]
  [
    set profit-list-dairy lput 0 profit-list-dairy
  ]
end

to update-price
  let n-years-average 3
  if year < year-brexit
  [
    ifelse ticks < length p-beef-list
    [
      set p-beef item ticks p-beef-list
    ]
    [
      set p-beef mean (sublist (reverse p-beef-list) 0 n-years-average)
    ]
    ifelse ticks < length p-dairy-list
    [
      set p-dairy item ticks p-dairy-list
    ]
    [
      set p-beef mean (sublist (reverse p-beef-list) 0 n-years-average)
    ]
    ifelse ticks < length p-hay-list
    [
      set p-hay item ticks p-hay-list
    ]
    [
      set p-hay mean (sublist (reverse p-hay-list) 0 n-years-average)
    ]
    ifelse ticks < length p-straw-list
    [
      set p-straw item ticks p-straw-list
    ]
    [
      set p-straw mean (sublist (reverse p-straw-list) 0 n-years-average)
    ]
    ifelse ticks < length annual-yield-per-cow-list
    [
      set annual-yield-per-cow item ticks annual-yield-per-cow-list
    ]
    [
      set annual-yield-per-cow mean (sublist (reverse annual-yield-per-cow-list) 0 n-years-average)
    ]
  ]
  if year = year-brexit and scenario != "no-brexit"
  [
    let base-p-beef mean (sublist (reverse p-beef-list) 0 n-years-average)
    let base-p-dairy mean (sublist (reverse p-dairy-list) 0 n-years-average)
    set p-hay mean (sublist (reverse p-hay-list) 0 n-years-average)
    set p-straw mean (sublist (reverse p-straw-list) 0 n-years-average)
    set annual-yield-per-cow mean (sublist (reverse annual-yield-per-cow-list) 0 n-years-average)
    let change-p-beef 0 ;; in percentage
    let change-p-dairy 0 ;; in percentage
    if scenario = "S1 FTA"
    [
      set change-p-beef 0.03;
      set change-p-dairy 0.01
    ]
    if scenario = "S2 WTO"
    [
      set change-p-beef 0.17
      set change-p-dairy 0.3
    ]
    if scenario = "S3 UTL"
    [
      set change-p-beef -0.45
      set change-p-dairy -0.1
    ]
    set p-beef base-p-beef * (1 + change-p-beef)
    set p-dairy base-p-dairy * (1 + change-p-dairy)
  ]
  ;show (word year ", " p-beef ", " p-dairy)
end

to export-holding-data
  let data-list (list (list "holding-code" "cattle-beef" "cattle-dairy" "calf-beef" "calf-dairy" "breeder-beef" "breeder-dairy" "service-bull" "cattle-other" "cattle-all"))
  foreach sort-on [holding-code] holdings
  [
    [this-holding]->
    let data []
    ask this-holding
    [
      set data lput holding-code data
      set data lput initial-cattle-beef data
      set data lput initial-cattle-dairy data
      set data lput initial-calf-beef data
      set data lput initial-calf-dairy data
      set data lput initial-breeder-beef data
      set data lput initial-breeder-dairy data
      set data lput initial-service-bull data
      set data lput initial-cattle-other data
      set data lput initial-cattle-all data
    ]
    set data-list lput data data-list
  ]
  csv:to-file "data.csv" data-list
end

;; TODO
to read-manager
  ask holdings
  [
    set manager? false
  ]
  file-open "dta-merged.csv"
  let var-names csv:from-row file-read-line
  let count-line 0
  let count-holding 0
  while [not file-at-end? ]
  [
    set count-line count-line + 1
    let row csv:from-row file-read-line
    let this-holding-code item (position "HOLDING_CODE" var-names) row
    let this-holding one-of holdings with [holding-code = this-holding-code]
    if this-holding != nobody
    [
      set count-holding count-holding + 1
      let this-manager item (position "ITEM538" var-names) row
      if this-manager = 1 or this-manager = 2
      [
        ask this-holding
        [
          set manager? true
        ]
      ]
      ask this-holding
      [
        set initial-manager? manager?
      ]
    ]
  ]
  file-close
  show (word "count-line = " count-line " count-holding = " count-holding " read-manager finished")
end

;; TODO
to read-tourism
  ask holdings
  [
    set tourism? false
  ]
  file-open "dta-merged.csv"
  let var-names csv:from-row file-read-line
  let count-line 0
  let count-holding 0
  while [not file-at-end? ]
  [
    set count-line count-line + 1
    let row csv:from-row file-read-line
    let this-holding-code item (position "HOLDING_CODE" var-names) row
    let this-holding one-of holdings with [holding-code = this-holding-code]
    if this-holding != nobody
    [
      set count-holding count-holding + 1
      let this-tourism item (position "ITEM2499" var-names) row
      if this-tourism = 1
      [
        ask this-holding
        [
          set tourism? true
        ]
      ]
      ask this-holding
      [
        set initial-tourism? tourism?
      ]
    ]
  ]
  file-close
  show (word "count-line = " count-line " count-holding = " count-holding " read-tourism finished")
end

to read-size
  file-open "size.csv"
  let var-names csv:from-row file-read-line
  let count-line 0
  let count-holding 0
  while [not file-at-end? ]
  [
    set count-line count-line + 1
    let row csv:from-row file-read-line
    let this-holding-code item (position "F_FAR_FARM" var-names) row
    let this-holding one-of holdings with [holding-code = this-holding-code]
    if this-holding != nobody
    [
      set count-holding count-holding + 1
      let this-area item (position "Shape_Area" var-names) row
      ask this-holding
      [
        set area this-area
      ]
    ]
  ]
  file-close
  show (word "count-line = " count-line " count-holding = " count-holding " read-tourism finished")
end

to update-off-farm-income
  if year < last-year-holding-data
  [
    set off-farm-income? item ticks off-farm-income-list ;; list starts from 2000
  ]
end

to update-succession
  ifelse year < last-year-holding-data
  [
    set successor? item ticks successor-list
  ]
  [
    if random-float 1 < annual-rate-succession-issue
    [
      set successor? false
    ]
  ]
end

;;holding procedure
to update-tourism
  ifelse tourism?
  [
    if random-float 1 < p-quit-tourism
    [
      set tourism? false
    ]
  ]
  [
    let range-distance range-tourism / km-per-patch ;; km / km-per-patch = n patches or distance
    let p-tourism-nearby 0
    let n-holdings-nearby count holdings with [distance myself < range-distance]
    if n-holdings-nearby > 0
    [
      set p-tourism-nearby count holdings with [distance myself < range-distance and tourism?] / n-holdings-nearby
    ]
    if random-float 1 < p-tourism-nearby * p-consider-tourism
    [
      set tourism? true
    ]
  ]
end

;;holding procedure
to update-manager
  ifelse cattle-all >= min-size-manager and profit-driven?
  [
    let range-distance range-manager / km-per-patch ;; km / km-per-patch = n patches or distance
    let p-manager-nearby 0
    let n-holdings-nearby count holdings with [distance myself < range-distance]
    if n-holdings-nearby > 0
    [
      set p-manager-nearby count holdings with [distance myself < range-distance and manager?] / n-holdings-nearby
    ]
    if random-float 1 < p-manager-nearby * p-consider-manager
    [
      set manager? true
    ]
  ]
  [
    set manager? false
  ]
end

;; holding scenario
to-report calculate-profit-beef
  let profit-beef 0
  if cattle-beef > 0
  [
    let own-feed-straw-per-cattle-beef own-feed-straw * (cattle-to-straw-beef * (cattle-all - cattle-dairy)) / (cattle-to-straw-dairy * cattle-dairy + cattle-to-straw-beef * (cattle-all - cattle-dairy)) / (cattle-all - cattle-dairy)
    let q-feed-straw 0
    if own-feed-straw-per-cattle-beef < cattle-to-straw-beef
    [
      set q-feed-straw (cattle-to-straw-beef - own-feed-straw-per-cattle-beef) * cattle-beef
    ]
    let own-feed-grass-per-cattle-beef own-feed-grass * (cattle-to-grass-beef * (cattle-all - cattle-dairy)) / (cattle-to-grass-dairy * cattle-dairy + cattle-to-grass-beef * (cattle-all - cattle-dairy)) / (cattle-all - cattle-dairy)
    let q-feed-grass 0
    if own-feed-grass-per-cattle-beef < cattle-to-grass-beef
    [
      set q-feed-grass (cattle-to-grass-beef - own-feed-grass-per-cattle-beef) * cattle-beef
    ]
    set profit-beef p-beef * cattle-beef - p-straw * q-feed-straw - p-hay * q-feed-grass
  ]
  report profit-beef
end

;; holding scenario
to-report calculate-profit-dairy
  let profit-dairy 0
  if cattle-dairy > 0
  [
    let income-per-cow p-dairy * annual-yield-per-cow / 100 ;; p-dairy is in pence
    let own-feed-straw-per-cattle-dairy own-feed-straw * (cattle-to-straw-dairy * cattle-dairy) / (cattle-to-straw-dairy * cattle-dairy + cattle-to-straw-beef * (cattle-all - cattle-dairy)) / cattle-dairy
    let q-feed-straw 0
    if own-feed-straw-per-cattle-dairy < cattle-to-straw-dairy
    [
      set q-feed-straw (cattle-to-straw-dairy - own-feed-straw-per-cattle-dairy) * cattle-dairy
    ]
    let own-feed-grass-per-cattle-dairy own-feed-grass * (cattle-to-grass-dairy * cattle-dairy) / (cattle-to-grass-dairy * cattle-dairy + cattle-to-grass-beef * (cattle-all - cattle-dairy)) / cattle-dairy
    let q-feed-grass 0
    if own-feed-grass-per-cattle-dairy < cattle-to-grass-dairy
    [
      set q-feed-grass (cattle-to-grass-dairy - own-feed-grass-per-cattle-dairy) * cattle-dairy
    ]
    set profit-dairy income-per-cow * cattle-dairy - p-straw * q-feed-straw - p-hay * q-feed-grass
  ]
  report profit-dairy
end

;; holding procedure
to update-decision-quit
  foreach (list "cattle-beef" "cattle-dairy" "calf-beef" "calf-dairy" "breeder-beef" "breeder-dairy" "service-bull" "other")
  [
    [cattle-type] ->
    hatch-decisions 1
    [
      set decision-maker myself
      set decision-object cattle-type
      set action "shrink-quit"
    ]
  ]
end

;; holding procedure
to update-decision-profit-cattle
  if last profit-list-beef > last but-last profit-list-beef * (1 + expand-buffer)
  [
    hatch-decisions 1
    [
     set decision-maker myself
     set decision-object "cattle-beef"
     set action "expand"
    ]
  ]
  if last profit-list-beef < last but-last profit-list-beef * (1 - shrink-buffer)
  [
    hatch-decisions 1
    [
     set decision-maker myself
     set decision-object "cattle-beef"
     set action "shrink"
    ]
  ]
  if last profit-list-dairy > last but-last profit-list-dairy * (1 + expand-buffer)
  [
    hatch-decisions 1
    [
     set decision-maker myself
     set decision-object "cattle-dairy"
     set action "expand"
    ]
  ]
  if last profit-list-dairy < last but-last profit-list-dairy * (1 - shrink-buffer)
  [
    hatch-decisions 1
    [
     set decision-maker myself
     set decision-object "cattle-dairy"
     set action "shrink"
    ]
  ]
end

;; holding procedure
to update-decision-profit-calf
   ifelse item (ticks + 1) n-cattle-list-beef > item ticks n-cattle-list-beef * (1 + expand-buffer)
   [
     hatch-decisions 1
     [
       set decision-maker myself
       set decision-object "calf-beef"
       set action "expand"
     ]
   ]
   [
     if item (ticks + 1) n-cattle-list-beef < item ticks n-cattle-list-beef * (1 - shrink-buffer)
     [
       hatch-decisions 1
       [
         set decision-maker myself
         set decision-object "calf-beef"
         set action "shrink"
       ]
     ]
   ]
   ifelse item (ticks + 1) n-cattle-list-dairy > item ticks n-cattle-list-dairy * (1 + expand-buffer)
   [
     hatch-decisions 1
     [
       set decision-maker myself
       set decision-object "calf-dairy"
       set action "expand"
     ]
   ]
   [
     if item (ticks + 1) n-cattle-list-dairy < item ticks n-cattle-list-dairy * (1 - shrink-buffer)
     [
       hatch-decisions 1
       [
         set decision-maker myself
         set decision-object "calf-dairy"
         set action "shrink"
       ]
     ]
   ]
end

to update-decision-profit-breeder
  ifelse item (ticks + 1) n-calf-list-beef > item ticks n-calf-list-beef * (1 + expand-buffer)
  [
    hatch-decisions 1
    [
      set decision-maker myself
      set decision-object "breeder-beef"
      set action "expand"
    ]
  ]
  [
    if item (ticks + 1) n-calf-list-beef < item ticks n-calf-list-beef * (1 - shrink-buffer)
    [
      hatch-decisions 1
      [
        set decision-maker myself
        set decision-object "breeder-beef"
        set action "shrink"
      ]
    ]
  ]
  ifelse item (ticks + 1) n-calf-list-dairy > item ticks n-calf-list-dairy * (1 + expand-buffer)
  [
    hatch-decisions 1
    [
      set decision-maker myself
      set decision-object "breeder-dairy"
      set action "expand"
    ]
  ]
  [
    if item (ticks + 1) n-calf-list-dairy < item ticks n-calf-list-dairy * (1 - shrink-buffer)
    [
      hatch-decisions 1
      [
        set decision-maker myself
        set decision-object "breeder-dairy"
        set action "shrink"
      ]
    ]
  ]
end

to read-price
  set p-beef-list []
  set p-dairy-list []
  set p-hay-list []
  set p-straw-list []
  set annual-yield-per-cow-list [] ;; liter
  let file-name (word "dataSSC/dta_price.csv")
  let dta csv:from-file file-name
  let headings first dta
  set dta but-first dta
  while [not empty? dta]
  [
    let data-line first dta
    set dta but-first dta
    (foreach headings data-line
      [
        [this-heading value ] ->
       if this-heading = "income per head beef"
       [
         set p-beef-list lput value p-beef-list
       ]
       if this-heading = "milk price per liter in pence"
       [
         set p-dairy-list lput value p-dairy-list
       ]
       if this-heading = "annual-yield-per-cow"
       [
         set annual-yield-per-cow-list lput value annual-yield-per-cow-list
       ]
       if this-heading = "price hay"
       [
         set p-hay-list lput value p-hay-list
       ]
       if this-heading = "price straw"
       [
         set p-straw-list lput value p-straw-list
       ]
      ]
    )
  ]
end

to update-decision-profit-other
 let expand? false
 let shrink? false
 let total-cattle-this-year item (ticks + 1) n-cattle-list-beef + item (ticks + 1) n-cattle-list-dairy + item (ticks + 1) n-calf-list-beef + item (ticks + 1) n-calf-list-dairy + item (ticks + 1) n-breeder-list-beef + item (ticks + 1) n-breeder-list-dairy + item (ticks + 1) n-service-bull-list
 let total-cattle-last-year item ticks n-cattle-list-beef + item ticks n-cattle-list-dairy + item ticks n-calf-list-beef + item ticks n-calf-list-dairy + item ticks n-breeder-list-beef + item ticks n-breeder-list-dairy + item ticks n-service-bull-list
 ifelse total-cattle-this-year > total-cattle-last-year * (1 + expand-buffer)
 [
   hatch-decisions 1
   [
     set decision-maker myself
     set decision-object "other"
     set action "expand"
   ]
 ]
 [
   if total-cattle-this-year < total-cattle-last-year * (1 - shrink-buffer)
   [
     hatch-decisions 1
     [
       set decision-maker myself
       set decision-object "other"
       set action "shrink"
     ]
   ]
 ]
end

to update-decision-profit-service-bull
 ifelse item (ticks + 1) n-breeder-list-beef + item (ticks + 1) n-breeder-list-dairy > (item ticks n-breeder-list-beef + item ticks n-breeder-list-dairy) * (1 + expand-buffer)
 [
   hatch-decisions 1
   [
     set decision-maker myself
     set decision-object "service-bull"
     set action "expand"
   ]
 ]
 [
   if item (ticks + 1) n-breeder-list-beef + item (ticks + 1) n-breeder-list-dairy < (item ticks n-breeder-list-beef + item ticks n-breeder-list-dairy) * (1 - shrink-buffer)
   [
     hatch-decisions 1
     [
       set decision-maker myself
       set decision-object "service-bull"
       set action "shrink"
     ]
   ]
 ]
end

;; decision procedure
to implement-decision
  let rate 0
  if action = "expand"
  [
    ifelse industrialization? and [manager?] of decision-maker
    [
      set rate rate-expand-manager
    ]
    [
      set rate rate-expand
    ]
  ]
  if action = "shrink"
  [
    ifelse industrialization? and [manager?] of decision-maker
    [
      set rate rate-shrink-manager
    ]
    [
      set rate -1 * rate-shrink
    ]
  ]
  if action = "shrink-quit"
  [
    set rate -1 * rate-shrink-quit
  ]
  if decision-object = "cattle-beef"
  [
    ask decision-maker
    [
      set cattle-beef round (cattle-beef * (1 + rate))
    ]
  ]
  if decision-object = "cattle-dairy"
  [
    ask decision-maker
    [
      set cattle-dairy round (cattle-dairy * (1 + rate))
    ]
  ]
  if decision-object = "calf-beef"
  [
    ask decision-maker
    [
      set calf-beef round (calf-beef * (1 + rate))
    ]
  ]
  if decision-object = "calf-dairy"
  [
    ask decision-maker
    [
      set calf-dairy round (calf-dairy * (1 + rate))
    ]
  ]
  if decision-object = "breeder-beef"
  [
    ask decision-maker
    [
      set breeder-beef round (breeder-beef * (1 + rate))
    ]
  ]
  if decision-object = "breeder-dairy"
  [
    ask decision-maker
    [
      set breeder-dairy round (breeder-dairy * (1 + rate))
    ]
  ]
  if decision-object = "service-bull"
  [
    ask decision-maker
    [
      set service-bull round (service-bull * (1 + rate))
    ]
  ]
  if decision-object = "cattle-other"
  [
    ask decision-maker
    [
      set cattle-other round (cattle-other * (1 + rate))
    ]
  ]
end

to update-total-size-cattle
  set n-cattle-list-beef lput sum [cattle-beef] of holdings n-cattle-list-beef
  set n-cattle-list-dairy lput sum [cattle-dairy] of holdings n-cattle-list-dairy
end

to update-total-size-calf
  set n-calf-list-beef lput sum [calf-beef] of holdings n-calf-list-beef
  set n-calf-list-dairy lput sum [calf-dairy] of holdings n-calf-list-dairy
end

to update-total-size-breeder
  set n-breeder-list-beef lput sum [breeder-beef] of holdings n-breeder-list-beef
  set n-breeder-list-dairy lput sum [breeder-dairy] of holdings n-breeder-list-dairy
end

to update-total-size-service-bull
  set n-service-bull-list lput sum [service-bull] of holdings n-service-bull-list
end

to update-total-size-other
  set n-cattle-list-other lput sum [cattle-other] of holdings n-cattle-list-other
end

to update-total-size-all
  set n-cattle-list-all lput sum [cattle-all] of holdings n-cattle-list-all
end

;; holding procedure
to update-size-group
  set cattle-all cattle-beef + cattle-dairy + calf-beef + calf-dairy + breeder-beef + breeder-dairy + service-bull + cattle-other
  if cattle-all >= cutoff-large-medium
  [
    set group 1
  ]
  if cattle-all < cutoff-medium-small
  [
    set group 3
  ]
  if cattle-all < cutoff-large-medium and cattle-all >= cutoff-medium-small
  [
    set group 2
  ]
end

to setup-holding-geography
  let holding-centroid gis:load-dataset ("dataGeo/holding_centroid.shp")
  gis:set-world-envelope
  (
    gis:envelope-union-of
    (gis:envelope-of holding-centroid)
  )
  (foreach gis:feature-list-of holding-centroid
    [
      [feature] ->
      let vertex item 0 (item 0 gis:vertex-lists-of (feature))
      let xy-list gis:location-of vertex
      ifelse not empty? xy-list
      [
        let this-patch patch (item 0 xy-list) (item 1 xy-list)
        let this-holding-code gis:property-value feature "F_FAR_FARM"
        let this-holding one-of holdings with [holding-code = this-holding-code]
        if this-holding != nobody
        [
          ask this-holding
          [
            set holding-patch this-patch
            move-to this-patch
          ]
        ]
      ]
      [
        show word "empty location: " gis:property-value feature "F_FAR_FARM"
      ]
    ]
   )
  update-holding-shape-size
end

to update-holding-shape-size
  ask holdings with [cattle-all > 0]
  [
    set shape "circle"
    if group = 1
    [
      set color red
      set size 4
    ]
    if group = 2
    [
      set color blue
      set size 2
    ]
    if group = 3
    [
      set color orange
      set size 1
    ]
  ]
  ask holdings with [cattle-all = 0]
  [
    set size 0
  ]
end

to setup-urban-rural
  let urban-rural-data gis:load-dataset ("dataGeo/SG_UrbanRural_2013_2014.shp")
  gis:set-world-envelope gis:envelope-of urban-rural-data
  (foreach gis:feature-list-of urban-rural-data
  [
    [this-urban-rural-data] ->
    let this-six-fold gis:property-value this-urban-rural-data "UR6FOLD"
    show (word "six fold: " this-six-fold)
    let this-patch-set patches gis:intersecting this-urban-rural-data
    if count this-patch-set > 0
    [
       ask this-patch-set
       [
         set six-fold this-six-fold
       ]
    ]
  ])
  show "setup-urban-rural finished"
end

to setup-country-region
  ask region-labels [die]
  let country-data gis:load-dataset ("dataGeo/UK2.shp")
  (foreach gis:feature-list-of country-data
  [
    [this-country-data] ->
    let this-patch-set patches gis:intersecting this-country-data
    if count this-patch-set > 0
    [
      let this-country-name gis:property-value this-country-data "NAME_1"
      let this-region-name gis:property-value this-country-data "NAME_2"
      show (word this-country-name ": " this-region-name)
      ask this-patch-set
      [
        set country-name this-country-name;; England, Scotland
        set region-name this-region-name ;; county name, eg, aberdeen
      ]
      create-region-labels 1
      [
        set region-label-name this-region-name
        set label region-label-name
        move-to patch mean [pxcor] of this-patch-set mean [pycor] of this-patch-set
        set size 0
      ]
    ]
  ])
 show "setup-country-region finished"
end

to setup-less-favoured-area
  let lfa-data gis:load-dataset ("SG_LessFavouredAreas_1997/SG_LessFavouredAreas_1997.shp")
  let i 0
  (foreach gis:feature-list-of lfa-data
  [
    [this-lfa-data] ->
    let this-patch-set patches gis:intersecting this-lfa-data
    if count this-patch-set > 0
    [
      set i i + 1
      if remainder i 100 = 0
      [
        show i
      ]
      ask this-patch-set
      [
        let lfa-value gis:property-value this-lfa-data "STATUS"
        let this-lfa 0
        if lfa-value = "Disadvantaged"
        [
          set this-lfa 1
        ]
        if lfa-value = "Severely Disadvantaged"
        [
          set this-lfa 2
        ]
        set lfa this-lfa
      ]
    ]
  ])
  show "setup-less-favoured-area finished"
end

to setup-patch-color
  ask patches with [lfa = 0 and region-name != 0][set pcolor green]
  ask patches with [lfa = 1 and region-name != 0][set pcolor yellow]
  ask patches with [lfa = 2 and region-name != 0][set pcolor brown]
  ask patches with [country-name = "England" or country-name = "Northern Ireland"][set pcolor gray + 1]
  ask patches with [region-name = 0][set pcolor cyan]
  ask patches with [six-fold = 1 or six-fold = 2][set pcolor gray - 2]
  gis:draw gis:load-dataset ("dataGeo/UK2.shp") 0.5
end


to run-all-poss-n-times
  foreach (list FALSE)
  [
    [this-succession-issue?]->
    foreach (list TRUE FALSE)
    [
      [this-leisure-farm?]->
      foreach (list TRUE FALSE)
      [
        [this-diversification?]->
        foreach (list TRUE FALSE)
        [
          [this-industrialization?]->
          let i 1
          while [i <= n-runs]
          [
            set scenario "S0 no brexit"
            set succession-issue? this-succession-issue?
            set leisure-farm? this-leisure-farm?
            set diversification? this-diversification?
            set industrialization? this-industrialization?
            run-till-2012
            let exp-name (word scenario "-" succession-issue? "-" leisure-farm? "-" diversification? "-" industrialization?)
            let file-farm (word "results/farm-" exp-name "-" i ".csv")
            let file-cattle (word "results/cattle-" exp-name "-" i ".csv")
            csv:to-file file-farm result-list-farm
            csv:to-file file-cattle result-list-cattle
            set i i + 1
            ]
          ]
        ]
      ]
    ]
end

to run-till-2012
  reset
  repeat 13
  [
    go
  ]
end

to get_ensembles
  let i 1
  while [i <= n-runs]
  [
    let j i + 10
    set scenario "S0 no brexit"
    run-till-2012
    let exp-name (word "ensembles-" succession-issue? "-" leisure-farm? "-" diversification? "-" industrialization?)
    let file-farm (word "results/farm-" exp-name "-" j ".csv")
    let file-cattle (word "results/cattle-" exp-name "-" j ".csv")
    csv:to-file file-farm result-list-farm
    csv:to-file file-cattle result-list-cattle
    set i i + 1
  ]
end
@#$#@#$#@
GRAPHICS-WINDOW
856
10
1357
740
-1
-1
0.8
1
10
1
1
1
0
1
1
1
0
500
0
720
1
1
1
ticks
30.0

BUTTON
10
23
137
56
NIL
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
165
24
228
57
NIL
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
261
25
324
58
NIL
reset
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

MONITOR
453
10
529
71
year
year
17
1
15

PLOT
10
114
239
280
n small farms
year
NIL
0.0
12.0
8000.0
8500.0
true
false
"" ""
PENS
"n small" 1.0 0 -16777216 true "" "plot count holdings with [group = 3]"

PLOT
246
114
474
280
n medium farms
NIL
NIL
0.0
12.0
5000.0
3500.0
true
false
"" ""
PENS
"default" 1.0 0 -16777216 true "" "plot count holdings with [group = 2]"

PLOT
11
293
238
458
n large farms
NIL
NIL
0.0
12.0
900.0
1000.0
true
false
"" ""
PENS
"default" 1.0 0 -16777216 true "" "plot count holdings with [group = 1]"

SWITCH
490
90
641
123
succession-issue?
succession-issue?
1
1
-1000

SLIDER
450
404
661
437
annual-rate-succession-issue
annual-rate-succession-issue
0
0.2
0.01
0.01
1
NIL
HORIZONTAL

SWITCH
693
55
823
88
make-movie?
make-movie?
1
1
-1000

BUTTON
692
14
800
47
NIL
make-video\n
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
13
66
120
99
NIL
run-till-2030
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

CHOOSER
539
13
677
58
scenario
scenario
"S0 no brexit" "S1 FTA" "S2 WTO" "S3 UTL"
0

PLOT
15
469
275
654
n cattle (thousand)
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"all" 1.0 0 -16777216 true "plot sum [cattle-all] of holdings / 1000" "plot sum [cattle-all] of holdings / 1000"
"beef" 1.0 0 -2674135 true "plot sum [cattle-beef + calf-beef + breeder-beef] of holdings / 1000" "plot sum [cattle-beef + calf-beef + breeder-beef] of holdings / 1000"
"dairy" 1.0 0 -1184463 true "plot sum [cattle-dairy + calf-dairy + breeder-dairy] of holdings / 1000" "plot sum [cattle-dairy + calf-dairy + breeder-dairy] of holdings / 1000"

PLOT
283
469
539
655
income per head
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"beef" 1.0 0 -2674135 true "plot p-beef" "plot p-beef"
"dairy" 1.0 0 -1184463 true "plot p-dairy * annual-yield-per-cow / 100" "plot p-dairy * annual-yield-per-cow / 100"

SWITCH
490
128
641
161
leisure-farm?
leisure-farm?
0
1
-1000

SWITCH
490
168
641
201
diversification?
diversification?
0
1
-1000

SWITCH
489
209
641
242
industrialization?
industrialization?
1
1
-1000

SLIDER
669
112
841
145
rate-expand
rate-expand
0
0.3
0.05
0.05
1
NIL
HORIZONTAL

SLIDER
668
152
842
185
rate-expand-manager
rate-expand-manager
0
0.3
0.1
0.05
1
NIL
HORIZONTAL

SLIDER
668
192
842
225
rate-shrink
rate-shrink
0
0.3
0.05
0.05
1
NIL
HORIZONTAL

SLIDER
669
230
842
263
rate-shrink-manager
rate-shrink-manager
0
0.3
0.05
0.05
1
NIL
HORIZONTAL

SLIDER
668
267
843
300
rate-shrink-quit
rate-shrink-quit
0
0.3
0.3
0.05
1
NIL
HORIZONTAL

PLOT
546
469
795
655
avg variable profit (thousand)
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"beef" 1.0 0 -2674135 true "" "plot mean [last profit-list-beef] of holdings with [last profit-list-beef != 0] / 1000"
"dairy" 1.0 0 -1184463 true "" "plot mean [last profit-list-dairy] of holdings with [last profit-list-dairy != 0] / 1000"

SLIDER
486
284
658
317
range-tourism
range-tourism
0
50
10.0
1
1
km
HORIZONTAL

SLIDER
486
322
659
355
range-manager
range-manager
0
50
15.0
1
1
km
HORIZONTAL

SLIDER
487
361
660
394
min-size-manager
min-size-manager
0
200
50.0
1
1
NIL
HORIZONTAL

SLIDER
675
363
847
396
p-consider-tourism
p-consider-tourism
0
1
0.2
0.1
1
NIL
HORIZONTAL

SLIDER
675
325
847
358
p-quit-tourism
p-quit-tourism
0
0.1
0.05
0.01
1
NIL
HORIZONTAL

SLIDER
675
399
848
432
p-consider-manager
p-consider-manager
0
1
0.2
0.1
1
NIL
HORIZONTAL

SLIDER
128
65
239
98
n-runs
n-runs
0
100
2.0
1
1
NIL
HORIZONTAL

BUTTON
247
66
444
99
NIL
run-all-scenarios-n-times
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
359
27
532
60
NIL
run-all-poss-n-times
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

@#$#@#$#@
## WHAT IS IT?

(a general understanding of what the model is trying to show or explain)

## HOW IT WORKS

(what rules the agents use to create the overall behavior of the model)

## HOW TO USE IT

(how to use the model, including a description of each of the items in the Interface tab)

## THINGS TO NOTICE

(suggested things for the user to notice while running the model)

## THINGS TO TRY

(suggested things for the user to try to do (move sliders, switches, etc.) with the model)

## EXTENDING THE MODEL

(suggested things to add or change in the Code tab to make the model more complicated, detailed, accurate, etc.)

## NETLOGO FEATURES

(interesting or unusual features of NetLogo that the model uses, particularly in the Code tab; or where workarounds were needed for missing features)

## RELATED MODELS

(models in the NetLogo Models Library and elsewhere which are of related interest)

## CREDITS AND REFERENCES

(a reference to the model's URL on the web if it has one, as well as any other necessary credits, citations, and links)
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.1.1
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
