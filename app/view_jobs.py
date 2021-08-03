from flask import Blueprint
from flask.templating import render_template
# from .jobscrawler import update_jobposts


jobs = Blueprint("jobs", __name__)


@jobs.route("/", methods=["POST", "GET"])
def job_searching():
    # remember to add "https://" before the web links
    sample_data = [
        {
            "title": "Sofrware Engineer", 
            "link": "https://sg.indeed.com/pagead/clk?mo=r&ad=-6NYlbfkN0AuWpd06JaTHFjvTB_5q6-0gBNCyrzTNez_CNw5GfFr-Uvaof5dLYkpXw27dWLYNm-xa2NTOhaWsJIcFGY_PviZ18DfiyayAnH2x4AQ-DXLnPuw41TvRlXrUJVBLV3RxCukWhyi27D9SKPicRKdGvisheEPs2OXimYc59LWcHe4aMiedoH8Fhs4mKK30vCW5Ov5n94vVtNitjdJLSrFDr9TOHJiWKB0bEOkiibfWXaLbhxpxontuwzvgpsYX6ktEvaBY4bwCGhOms9BMJjPrnt7zo964QIiEAioF1O00mo4mFObxKwnOmJEr9cn-j-JkBlbuBO7L22xvkmSu5ypGROq_uae_fR_sZLxGytpJh8a9rByaANZ4TPYuJwE0AxPr0Lo3ZoKyGsWDNoEPYLaiEsgAzE2agvbC48T-1WK65vUmIBpxvq7n_sxs6TPOWZVou29BqqsJt1dHpXnXXQFF7sN4iNunqylGFJYGyeRg4fT6eLogJtC8KZqfW1EY4oXlKHsuAQZeqCM-PIhrmv0rYe-jOYFcJ4rL_CZsu55T_X304OFuzsZsmuDVq3Xovh928r5wB_FC1_TmkuHn5092DcMnqnKbX3f4DoKagFRUIn0CdzGZDXOgtAo-SLcROBx6EmZ6kbZjsvesYMHjNVc5YnD_f8p8oz9q-eNi1BMikbAzvUsqrlDwMKXcT_WS3Y4at-RQx_aKtgAgPe8jXEJsm0DH7GhpJI7y8f11owZdH4vl5QAaVJIGUL-ytiQBS-st7g=&p=0&fvj=0&vjs=3",
            "company": "SOFTENGER (SINGAPORE) PTE. LTD.",
            "salary": "$5000 - $6500 a month",
            "date": "2021-07-31"
        },
        {
            "title": "[EIPIC] Finance Executive", 
            "link": "https://sg.indeed.com/pagead/clk?mo=r&ad=-6NYlbfkN0AuWpd06JaTHFjvTB_5q6-0gBNCyrzTNez_CNw5GfFr-Uvaof5dLYkpQptHyIobf6wgmBdiqDP19eQfjBdkjP-eFEFNCevFTa36BnNQhcTk35iZlzBtnzuQ5xzVCsqGiEkrCEROfIb4oaoi0UStZrC6hN56Ieg2DFZ8rAfbGovtylZHntBJB1ZzVaKbd_vNxmm9g8XQ06EDSQsxxl4iwFNhJeIR2z6IeF3bO8626Mt47OHDzqI_jDGon2mFybJNpLByVeSg5ZydvwvE97_ZgeUEsQ6kxoILug_lWqlBeSzHTdKveI8ytiCGAu8t6wFc2IXXdvo9ECXhI10tpB3cE1Tutx5jH-IrlA98Fhfi7qe2qHqZTLRX6zp5vqIqdpcc0xTNg5JPCiQP4IcCpSBDlNeWTjOzRGrKbiaYTZArjRo8lob5V90yfC1u5c1lbTXhSUz6nFchfqN243nxQrI6_Zx61JoTUgewRhXDeCysf2DHVSpIJWi6hnQtQOyvCe5x-rl_O5narKrV6HPMD4mXwaeXYg2LEkKcmgu9GBWFLjSeeiE3nBX7nuMIIoiTyTOtOhE7NXRYqiZhujke9OVKSlI3VzkxlnRMdn7LdIBuov3GJFU49BX7K_k6lpC_cg-kMve3Uqj8D9rUwgahMF2AYTtFJ73auSWE0HefQw32IjX6SwW8jmi0jHJ67fuKev6jwGUII2-Gp1Oz3p4pcjEBvDzaXsLhBocS1o9kaxznhXmVtShnwoUNQcSlN1uiJpfDL25mWLLGFsr49TPRalzEog_PClS2CDAHF3wGfutzmP08VKkhml6i_EWy1zIRkOaYyY8=&p=1&fvj=0&vjs=3",
            "company": "THYE HUA KWAN MORAL CHARITIES LIMITED",
            "salary": "$2510 - $3030 a month",
            "date": "2021-07-31"
        },
        {
            "title": "Sofrware Engineer", 
            "link": "https://sg.indeed.com/rc/clk?jk=254952268b4e141e&fccid=8975b9f5b98c2e9d&vjs=3",
            "company": "A2000 Solutions Pte Ltd",
            "salary": "not given",
            "date": "2021-08-01"
        },
        {
            "title": "Solution Sales Consultant", 
            "link": "https://sg.indeed.com/rc/clk?jk=af7b169c38091b05&fccid=8975b9f5b98c2e9d&vjs=3",
            "company": "A2000 Solutions Pte Ltd",
            "salary": "not given",
            "date": "2021-08-01"
        },
        {
            "title": "ERP Implementation Specialists", 
            "link": "https://sg.indeed.com/rc/clk?jk=11607ef578dcf2e2&fccid=8975b9f5b98c2e9d&vjs=3",
            "company": "A2000 Solutions Pte Ltd",
            "salary": "not given",
            "date": "2021-08-01"
        }
    ]
    return render_template("job_search_test.html", posts=sample_data)