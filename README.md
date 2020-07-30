# JT2
Download + store game and training data. Training and playing mechanism. Numerical and visual analytics.




## v0.6 [20/68]
* ~~Fix play to move long lines to next line [1]~~
* ~~When parsing replay, record DD status [5]~~
  * ~~Discount DD questions from modifying coryat when wrong [3]~~
* ~~When parsing replay, save correct/incorrect data [5]~~
  * ~~With corr/incorr data, calculate team performance metrics by episode/round [3]~~
    * ~~With player perform metrics by episode, analyze by getting my performamces relative to distribution [3]~~
* Identify other mining sources [2]
  * Implement mining on other sources [8]
* Develop plan to refactor minesn [3]
  * Refactor minesn [8]
* Develop visualization plan [3]
  * Implement visualization plan [5]
* Build training plan [5]
  * Implement training plan [8]
* For answers in corpus, mined data, augment from Wikipedia for training [5]
* Develop analysis plan [5]
  * Implement analysis plan [8]
* Build central UI from which play, train, analyze derive [8]

## To v1
* Refactoring [5]
* Full function documentation [5]
* Rename modules+functions to be explicit and intuitive [5]
* Add src/[packages] and update imports [5]
* Lint [5]

## Prospective v2
* Add URL links to DB table
* Better download logic
* Essentially, there is a bug in download that prevents update.
   * To fix, must write season urls to own table, episode URLs to own table, then mark episodes as not needed for update once downloaded
* Auto-scheduler on Mac and Windows with appropriate logging
* Move args to click (import click)
