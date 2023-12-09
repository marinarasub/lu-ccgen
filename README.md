# CCGen

## Chinese Character Generator

I had a hard time finding a Chinese character worksheet generator (田字格字帖产生器/田字格字帖產生器) which supported custom fonts, so here we go.

Dependencies:

- Python 3.10
- fpdf2 (`pip install fpdf2`)

Run with `python ccgen.py <options> <character list>`

Example:

``` sh
python ccgen.py  --nchar 6 --nbox 10 --font "TW-Kai Regular" --title "Daily Practice" 田字格字帖產生器
```

I suggest downloading a font you want to practice and supplying the `--font` option.

The code is public domain.