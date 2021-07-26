# Download public paper from emerald

## Install requirements
> pip install -r requirements.txt

## Get cookies
1. Login account and visit [a emerald paper link](https://www.emerald.com/insight/content/doi/10.1108/AAAJ-02-2019-3890/full/html), make sure you have access to the full paper.
2. Open developer tool of the browser: Application -> Cookies
3. Copy all Key:Value pairs to `cookies.py`

## Download papers with cookie
> python download.py --save_dir . --auth_by_cookie True

## Download open access papers (cookie not required)
> python download.py --save_dir .

## convert to jsonl
> python csv2jsonl.py --csv_dir . --jsonl_filename emerald.jsonl

