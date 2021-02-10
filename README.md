# Download public paper from emerald

## Install requirements
> pip install -r requirements.txt

## Get cookies
1. Login account and visit [a emerald paper link](https://www.emerald.com/insight/content/doi/10.1108/AAAJ-02-2019-3890/full/html) to check the fulltext
2. Open developer tool of the browser: Application -> Cookies
3. Copy all Key:Value pairs to `cookies.py`

## Download to csv
> python download.py --save_dir . --auth_by_cookie True

### to skip open access and pitt access journals
> python download.py --save_dir . --auth_by_cookie True --skip_open_access_and_pitt_authed True


## convert to jsonl
> python csv2jsonl.py --csv_dir . --jsonl_filename emerald.jsonl

