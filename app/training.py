examples = """
# Sản phẩm tiêu biểu tại 7-eleven và giá?
MATCH path = (a:Property {value: 'price_711'})-[:INIT]->(b:Price) 
MATCH path2 = (c:Property {value: 'product_711'})-[:INIT]->(d:Product) 
RETURN path, path2 LIMIT 20
# Tôi muốn nhiều thông tin hơn 
MATCH path = (a:Property {value: 'price_711'})-[:INIT]->(b:Price) 
MATCH path2 = (c:Property {value: 'product_711'})-[:INIT]->(d:Product) 
RETURN path, path2 LIMIT 40
# Giá các sản phẩm tiêu biểu tại Winmart?
MATCH path = (a:Property {value: 'product_winmart'})-[:INIT]->(b:Product) 
MATCH path2 = (c:Property {value: 'product_winmart'})-[:INIT]->(d:Product) 
RETURN path, path2 LIMIT 20
# Tôi muốn nhiều thông tin hơn
MATCH path = (a:Property {value: 'product_winmart'})-[:INIT]->(b:Product) 
MATCH path2 = (c:Property {value: 'price_winmart'})-[:INIT]->(d:Price) 
RETURN path, path2 LIMIT 40
# Thông tin khuyến mãi tại 7-eleven
MATCH path = (a:Property {value: 'promotion_711'})-[:INIT]->(b:Promotion) 
MATCH path = (a:Property {value: 'product_711'})-[:INIT]->(b:Product) 
RETURN path, path2 LIMIT 10
# Thông tin khuyến mãi tại Winmart
MATCH path = (a:Property {value: 'promotion_winmart'})-[:INIT]->(b:Promotion) 
MATCH path = (a:Property {value: 'product_winmart'})-[:INIT]->(b:Product) 
RETURN path, path2 LIMIT 10
# Sản phẩm tiêu biểu tại lotte và giá?
MATCH path = (a:Property {value: 'price_lotte'})-[:INIT]->(b:Price) 
MATCH path2 = (c:Property {value: 'product_lotte'})-[:INIT]->(d:Product) 
RETURN path, path2 LIMIT 20
# Thông tin khuyến mãi tại lotte
MATCH path = (a:Property {value: 'promotion_lotte'})-[:INIT]->(b:Promotion) 
MATCH path = (a:Property {value: 'product_lotte'})-[:INIT]->(b:Product) 
RETURN path, path2 LIMIT 10
"""

responses = ["Sau đây là giá của một số sản phẩm tại 7-eleven bạn có thể tham khảo: \n - Cà phê kem muối có giá 20k, 25k cho trà đào/ trà vải/ trà nhãn mật ong. \n - 660k 1 chai chống nắng senka uv milk. \n - 125k cherry mỹ hộp 250gr. \n \n Ngoài ra, chỉ 20k bánh mì pate, từ 300k hộp quà trái cây. Bạn cũng có thể tham khảo dâu tây hàn quốc 250gr: 129k hay bánh su kem xoài 14k/hộp.",
             "Cảm ơn bạn đã quan tâm, hiện 7-eleven còn nhiều sản phẩm với mức giá hấp dẫn khác như: \n - 41k trứng gà ta v.food 10 quả. \n - 19k khóm cắt sẵn. \n Ngoài ra còn có hộp sushi inari lục bảo 40k, trà tắc khổng lồ 10k hay trà oolong nhài sữa từ 20k. \n \n  Ngoài ra, 116k táo breeze túi 1kg, 29k burger trứng jambon phô mai cùng nhiều sản phẩm khác. \n \n Ghé 7-eleven để mua sắm với mức giá ưu đãi.",
             "Giá bán của một số sản phẩm tại Winmart: \n - Lê Hàn Quốc nhập khẩu 64.900đ/kg. \n - Bánh quy cosy thập cẩm socola/rắc hạt 336g: 74.500đ/hộp. \n - Bánh Danisa gold 279.000đ/hộp \n - 149.900đ/hộp 250gr dâu hàn quốc. \n - 199.900đ/kg nho đen mỹ. \n \n Bạn cũng có thể tham khảo mận đá: 39.900đ/kg, bưởi diễn: 19.900đ/quả, bia Carlsberg 330ml: 462.000đ/thùng cùng nhiều sản phẩm khác.",
             "Cảm ơn bạn đã quan tâm, hiện hệ thống cửa hàng Winmart còn nhiều sản phẩm với mức giá hấp dẫn khác như: \n - 159.000đ/chai dầu gội clear 9 loại thảo dược sạch gàu 630g. - \n 49.000đ/lốc giấy vệ sinh winmart home 10 cuộn 3 lớp không lõi. \n - 24.500đ/hộp kim chi dưa cải bibigo. \n - 9.300đ/lon nước giải khát coca 330/320ml. \n - 29.900đ/chai nước mắm chinsu hương cá hồi 500ml. \n \n Cùng nhiều sản phẩm khác với mức giá hấp dẫn như 23.800đ/lốc 4 sữa trái cây lif kin hương cam/nho 180ml, 12.000đ/hộp bánh dinh dưỡng afc vị caramel flan 125g. \n \n Ghé hệ thống cửa hàng Winmart để mua sắm với mức giá ưu đãi.",
             "Hiện tại, 7-eleven đang có một số khuyến mãi hấp dẫn. Bạn có thể nhận được một túi 7-eleven miễn phí, hoặc một chai Nutriboost cam/dâu 297ml miễn phí. Ngoài ra, bạn còn có cơ hội được tặng gối bông tea+ oolong size lớn, tặng nutriboost cookies hoặc tặng ly rap việt. Ngoài ra, còn có các khuyến mãi giảm giá từ 3k đến 14k hay các chương trình đồng giá 20k. Cuối cùng, bạn cũng có thể nhận được một topping miễn phí.  Ghé 7-eleven để mua sắm với mức giá ưu đãi.",
             "Tại chuỗi cửa hàng Winmart đang có các chương trình khuyến mãi sau. Khuyến mãi giảm giá lên tới 33%, khuyến mãi mua 1 tặng 1. Ngoài ra, bạn còn có cơ hội nhận ngay combo quà ly giữ nhiệt và gối tựa cổ, nhận ngay một bộ lì xì xịn mịn. Ngoài ra, còn có các khuyến mãi giảm giá 50%, giảm sốc 20%. Cuối cùng, bạn có thể được tặng thêm 1 lon strongbow đào.  Ghé Winmart để mua sắm với mức giá ưu đãi"]

cypher_output = ["CALL {MATCH path = (c:Property {value: 'product_711'})-[:INIT]->(d:Product) RETURN path LIMIT 10} CALL {MATCH path2 = (a:Property {value: 'price_711'})-[:INIT]->(b:Price) RETURN path2 LIMIT 10} RETURN path, path2",
                 "CALL {MATCH path = (c:Property {value: 'product_711'})-[:INIT]->(d:Product) RETURN path LIMIT 30} CALL {MATCH path2 = (a:Property {value: 'price_711'})-[:INIT]->(b:Price) RETURN path2 LIMIT 30} RETURN path, path2",
                 "CALL {MATCH path = (c:Property {value: 'product_winmart'})-[:INIT]->(d:Product) RETURN path LIMIT 10} CALL {MATCH path2 = (a:Property {value: 'price_winmart'})-[:INIT]->(b:Price) RETURN path2 LIMIT 10} RETURN path, path2",
                 "CALL {MATCH path = (c:Property {value: 'product_winmart'})-[:INIT]->(d:Product) RETURN path LIMIT 30} CALL {MATCH path2 = (a:Property {value: 'price_winmart'})-[:INIT]->(b:Price) RETURN path2 LIMIT 30} RETURN path, path2",
                 "CALL {MATCH path = (c:Property {value: 'promotion_711'})-[:INIT]->(d:Promotion) RETURN path LIMIT 10} CALL {MATCH path2 = (a:Property {value: 'product_711'})-[:INIT]->(b:Product) RETURN path2 LIMIT 10} RETURN path, path2",
                 "CALL {MATCH path = (c:Property {value: 'promotion_winmart'})-[:INIT]->(d:Promotion) RETURN path LIMIT 10} CALL {MATCH path2 = (a:Property {value: 'product_711'})-[:INIT]->(b:Product) RETURN path2 LIMIT 10} RETURN path, path2"]


cypher_test = ["MATCH path = (a:Property {value: 'price_711'})-[:INIT]->(b:Price) MATCH path2 = (c:Property {value: 'product_711'})-[:INIT]->(d:Product) RETURN path, path2 LIMIT 20",
                 "MATCH path = (a:Property {value: 'price_711'})-[:INIT]->(b:Price) MATCH path2 = (c:Property {value: 'product_711'})-[:INIT]->(d:Product) RETURN path, path2",
                 "MATCH path = (a:Property {value: 'product_winmart'})-[:INIT]->(b:Product) MATCH path2 = (c:Property {value: 'product_winmart'})-[:INIT]->(d:Product) RETURN path, path2 LIMIT 30",
                 "MATCH path = (a:Property {value: 'product_winmart'})-[:INIT]->(b:Product) MATCH path2 = (c:Property {value: 'price_winmart'})-[:INIT]->(d:Price) RETURN path, path2",
                 "MATCH path = (a:Property {value: 'promotion_711'})-[:INIT]->(b:Promotion) MATCH path = (a:Property {value: 'product_711'})-[:INIT]->(b:Product) RETURN path, path2 LIMIT 10",
                 "MATCH path = (a:Property {value: 'promotion_winmart'})-[:INIT]->(b:Promotion) MATCH path = (a:Property {value: 'product_winmart'})-[:INIT]->(b:Product) RETURN path, path2 LIMIT 10"]