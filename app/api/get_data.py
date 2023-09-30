from app.api.tasks2 import search_product

product_id = "175931038234218"
res = search_product.delay(product_id)
while True:
    if res.ready() == True:
        break
    print(res.get())

app.send_task('your_app.your_coroutine_task', args=[param1_value, param2_value])
