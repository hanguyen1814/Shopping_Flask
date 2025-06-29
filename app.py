from flask import Flask, render_template, request, redirect, url_for, session
from handle import track, pricetrack, aio, getvoucher
import re, os, json, requests
from urllib.parse import urlparse, parse_qs
import threading
import time

# Use absolute path for voucherFile
base_dir = os.path.dirname(os.path.abspath(__file__))
voucherFile = os.path.join(base_dir, 'data', 'vouchers.json')

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Cần thiết để sử dụng session


def read_voucher_file():
    try:
        with open(voucherFile, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error in read_voucher_file: {e}")
        return {"time": "Error", "data": []}

    
# Hàm giả lập xử lý dữ liệu
def get_voucher_info(links):
    data = {}
    for url in links:
        query_params = parse_qs(urlparse(url).query)
        promotion_id = query_params.get('promotionId', [None])[0]
        signature = query_params.get('signature', [None])[0]
        if promotion_id and signature:
            data[promotion_id] = signature

    results = track.trackVouchers(data)
    return results


def getIdItem(link: str) -> dict:
    try:
        get = aio.process_link_pee(link)

        if get != 0:
            [shopid, itemid] = get
            print(f"Shop ID: {shopid}, Item ID: {itemid}")
            return f"https://shopee.vn/NCH-i.{shopid}.{itemid}"
        else:
            raise ValueError("Shop ID and Item ID not found in the link")

    except Exception as e:
        print(f"Error in getIdItem: {e}")
        return None


@app.route("/tracks", methods=["GET", "POST"])
def tracks():
    if request.method == "POST":
        links = request.form.get("token")  # Lấy dữ liệu từ form
        if links:
            link_list = links.splitlines()[:10]  # Tối đa 10 link
            session["voucher_info"] = get_voucher_info(link_list)  # Lưu vào session
        return redirect(url_for("tracks"))  # Redirect để tránh resubmit form

    # Lấy dữ liệu từ session (nếu có)
    voucher_info = session.pop("voucher_info", None)
    return render_template("tracks.html", voucher_info=voucher_info)

# tracuu.html
@app.route("/tracuu", methods=["GET", "POST"])
def tracuu():
    if request.method == "POST":
        link = request.form.get("token")
        if link:
            id_item = getIdItem(link)
            print(f"Item: {id_item}")
            if id_item != None:
                session["product_info"] = pricetrack.all(id_item)
        return redirect(url_for("tracuu"))

    product_info = session.pop("product_info", None)
    return render_template("tracuu.html", product_info=product_info)

#rutgon.html
@app.route("/rutgon", methods=["GET", "POST"])
def rutgon():
    if request.method == "POST":
        text = request.form.get("rutgon")
        if text:
            result = aio.process_text(text)
            session["result"] = result
        
        return redirect(url_for("rutgon"))

    result = session.pop("result", None)
    return render_template("rutgon.html", result=result)

##vouchers.html
@app.route("/vouchers", methods=["GET"])
def vouchers():
    data = read_voucher_file()
    return render_template("vouchers.html", data=data)


# livexu.html
@app.route("/livexu", methods=["GET"])
def livexu():
    return render_template("livexu.html")
    
# flashsale.html
@app.route("/flashsale", methods=["GET", "POST"])
def flashsale():
    try:
        session_id = request.args.get('session')  # Default session ID if not provided
        if session_id == '':
            try:
                url = "https://api.nghienshopping.online/get/sessions/with-products"
                response = requests.request("GET", url, headers={})
                res = response.text
                data = json.loads(res)
                return render_template("flashsale.html", data={'sessions': data, 'products': []})
            except Exception as e:
                print(f"Error in flashsale: {e}")
                return render_template("flashsale.html", data={'sessions': [], 'products': []})
        url = f"https://api.nghienshopping.online/get/sessions/{session_id}/products?limit=all"
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers)
        print('Get flashsale OK!')
        return render_template("flashsale.html", data=json.loads(response.text))
    except Exception as e:
        print(f"Error in flashsale: {e}")
        return render_template("flashsale.html", data={'sessions': [], 'products': []})

def call_voucherPee_periodically():
    while True:
        getvoucher.voucherPee()
        time.sleep(3600)  # Sleep for 30 minutes

# Start the background thread
threading.Thread(target=call_voucherPee_periodically, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
