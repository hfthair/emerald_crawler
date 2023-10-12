
**New!!** The dataset is now available at [Hugging Face 🤗](https://huggingface.co/datasets/memray/FacetSum)

# Crawler code for downloading Emerald papers

## FacetSum dataset
Paper: ACL 2021, [Bringing Structure into Summaries: a Faceted Summarization Dataset for Long Scientific Documents](https://aclanthology.org/2021.acl-short.137.pdf)

Over 60k Emerald journal articles (long documents) with faceted summaries (purpose, method, findings, and value).

Train: 46,289 / Dev: 6,000 / Test: 6,000 / OA-Test: 2,243


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

## Convert to jsonl
> python csv2jsonl.py --csv_dir . --jsonl_filename emerald.jsonl

## For BARTFacet Finetuning
For fine tune code and model output, please visit this repository [Finetuning_BART_for_FACET_Summarization](https://github.com/khushsi/Finetuning_BART_for_FACET_Summarization)


## To cite FacetSum
```
@inproceedings{meng2021facetsum,
  title={Bringing Structure into Summaries: a Faceted Summarization Dataset for Long Scientific Documents},
  author={Meng, Rui and Thaker, Khushboo and Zhang, Lei and Dong, Yue and Yuan, Xingdi and Wang, Tong and He, Daqing},
  booktitle={Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 2: Short Papers)},
  pages={1080--1089},
  year={2021}
}
```
