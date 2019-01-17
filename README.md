# NFL-Big-Data-Bowl-Submission
## by Sam Setegne

# Table of Contents

# Introduction

/Data/ folder in root directory should contain all data from https://github.com/nfl-football-ops/Big-Data-Bowl

## ETL on Raw Tracking Data
![](http://yuml.me/diagram/plain;dir:td;scale:150/class/[Tracking%20Data{bg:seagreen}]->[Completed%20Passes],[Tracking%20Data]->[Incomplete%20Passes],[Completed%20Passes]->[Identify%20Catch%20Receiver%20&%20Closest%20Corner],[Identify%20Catch%20Receiver%20&%20Closest%20Corner]->[Calculate%20Catch%20Separation%20(Distance%20between%20receiver%20and%20closest%20defender%20at%20catch%20frame)],[Calculate%20Catch%20Separation%20(Distance%20between%20receiver%20and%20closest%20defender%20at%20catch%20frame)]->[Identify%20Routes%20of%20Each%20Receiver|X-Route%20options:;Short;Medium;Deep|Y-Route%20Options:;Stop;Slant;Flat;Out;In;Post;Corner;Fly],[Identify%20Routes%20of%20Each%20Receiver|X-Route%20options:;Short;Medium;Deep|Y-Route%20Options:;Stop;Slant;Flat;Out;In;Post;Corner;Fly]->[Create%20a%20Main%20Modeling%20Dataset],[Play%20Data]-.->[Create%20a%20Main%20Modeling%20Dataset],[Create%20a%20Main%20Modeling%20Dataset]->[Prepare%20Data|Features:;Target's%20X-Route;Target's%20Y-Route;2nd%20Receiver's%20X-Route;2nd%20Receiver's%20Y-Route;3rd%20Receiver's%20X-Route;3rd%20Receiver's%20Y-Route;4th%20Receiver's%20X-Route;4th%20Receiver's%20Y-Route;Down;Yards-To-Go;Offense%20Formation;Defenders%20in%20The%20Box;Pass%20Rushers;Offense%20Personnel;Defense%20Personnel|Label:;Catch%20Separation%20(yds){bg:steelblue}] "yUML")

## Preparing Data & Training KNN Model
![](http://yuml.me/diagram/plain;dir:lr;scale:150/class/[Modeling%20Dataset{bg:steelblue}]->[One%20hot%20encode%20Features],[One%20hot%20encode%20Features]->[Train-Test%20Split%20(70-30)],[Train-Test%20Split%20(70-30)]->[Min-Max%20Scaler;(Range=0%20to%201)],[Min-Max%20Scaler;(Range=0%20to%201)]->[x_train],[Min-Max%20Scaler;(Range=0%20to%201)]->[y_train],[x_train]->[K-Nearest-Neighbor%20Regressor],[y_train]->[K-Nearest-Neighbor%20Regressor],[K-Nearest-Neighbor%20Regressor]->[Final%20Trained%20Model{bg:salmon}] "yUML")

## Functional Flow of Catch Separation Model API
![](http://yuml.me/diagram/plain;dir:lr;scale:150/class/[Analyst{bg:tan}]->[Pre-snap%20Information{bg:springgreen}],[Pre-snap%20Information]->[Catch%20Separation%20API{bg:tomato}],[Catch%20Separation%20API]->[Scoring%20Engine{bg:red}],[Scoring%20Engine]->[Predicted%20Catch%20Separation{bg:gold}],[Predicted%20Catch%20Separation]->[Catch%20Separation%20API],[Catch%20Separation%20API]->[Analyst] "yUML")
