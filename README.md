# Dream Garden

## สำหรับเพื่อนร่วมทีม (How to Git)

### 1. การดึงโค้ดไปใช้ครั้งแรก (Clone)
```bash
git clone [URL-PROJECT]
git checkout develop
# 🌸 Dream Garden - Flower Planting Game 🌸

## 📖 ภาพรวมของโปรแกรม (Overview)
Dream Garden เป็นแอปพลิเคชันเกมส์ปลูกดอกไม้ที่สร้างด้วยเฟรมเวิร์ก Kivy โดยผู้เล่นสามารถเลือกเมล็ดพันธุ์ดอกไม้ที่ต้องการปลูก (เช่น ทานตะวัน กุหลาบ ทิวลิป กล้วยไม้ กระบองเพชร เห็ด) และใช้การกระทำต่างๆ เช่น รดน้ำ (Water), ให้แสงแดด (Sun), และใส่ปุ๋ย (Fertilizer) เพื่อให้ต้นไม้เจริญเติบโต 
ผู้เล่นต้องดูแลต้นไม้ให้ถูกวิธีตามความชอบของแต่ละสายพันธุ์ภายในระยะเวลาที่กำหนด (6 วัน / 6 เทิร์น) เพื่อให้ดอกไม้โตเต็มที่ร้อยเปอร์เซ็นต์ หากปลูกสำเร็จจนเติบโตเต็มที่ ดอกไม้จะถูกปลดล็อคและบันทึกสะสมในหน้า Catalog (My Garden Collection) ของผู้เล่น

## 🚀 วิธีการรันโปรแกรม (How to Run)
1. ติดตั้ง Python (แนะนำเวอร์ชัน 3.8-3.11)
2. ติดตั้งไลบรารี Kivy ผ่านตัวจัดการแพ็กเกจ:
   ```bash
   pip install kivy
   ```
3. เปิด Terminal หรือ Command Prompt นำทางไปที่โฟลเดอร์โปรเจกต์นี้
4. รันคำสั่งโปรแกรม:
   ```bash
   python main.py
   ```

## 👩‍💻 คำอธิบายการทำงานใน Code (Code Explanation)
โค้ดในโปรเจกต์นี้ถูกออกแบบมาเพื่อครอบคลุมข้อกำหนดเงื่อนไขของ Assignment ครบทุกเกณฑ์ โดยแบ่งออกเป็นสองส่วนหลัก:

### 1. KV Language (UI Design & Layouts) - รวมมีมากกว่า 48 Widgets
มีการใช้ Widget ในการสร้างหน้าจอต่างๆ และโครงสร้าง UI แยกไว้ในไฟล์ `garden.kv`:
- `MenuScreen`: เมนูหลัก มีปุ่มเลือกว่าจะเริ่มเกม ดูร้านค้า (Shop) หรือดูวิธีเล่นพร้อม Image เบื้องหลัง (9 Widgets)
- `LevelScreen`: ระบบเลือกพืชพันธุ์ที่ต้องการจะดูแล โดยมีโครงข่ายของ `GridLayout` (10 Widgets)
- `GameScreen`: แสดงแถบ ProgressBar หลอดความก้าวหน้าการเติบโต Label สำหรับแสดง Money และ Stamina, `Scatter` widget สำหรับควบคุมภาพต้นไม้, และปุ่ม Action สำหรับรดน้ำตากแดดที่รวมใน `GridLayout` (15 Widgets)
- `ShopScreen`: หน้าร้านค้าสำหรับผู้เล่นซื้อเมล็ดพันธุ์โดยใช้เงินที่มี (8 Widgets)
- `CollectionScreen`: แสดงผลดอกไม้ที่เก็บสะสมเมื่อเล่นเกมชนะ (5 Widgets)

### 2. Python Logic (Callbacks & Application State) - รวมมีมากกว่า 20 Callbacks
มีการใช้ Property Binding และ Action Callbacks ในตัวของ `main.py` เช่น:
- **Property Binding**: นำ `growth_progress` มาใช้กับฟังก์ชัน `on_growth_change` 
  เพื่อให้เมื่อกดรดน้ำหลอดโตขึ้น รูปภาพดอกไม้ก็จะเปลี่ยนสเตจการเติบโตอัตโนมัติ 
- **Action Callbacks**:
  - Callback ฟังก์ชันรดน้ำ (`water_plant`), ใส่ปุ๋ย (`fertilize_plant`), พรวนดิน (`till_soil`)
  - Callback เรียกดู Popup วิธีเล่น (`show_how_to_play` > `popup.dismiss`)
  - Callback สำหรับหน้าร้านค้า (`buy_seed`, `buy_item`) 
  - Callback ควบคุมการสลับหน้า (Screen Transition) มากกว่า 5 แห่ง (e.g. `app.root.current`)

### 3. ระบบเกม (Game Logic)
- **State Management:** แต่ละต้นไม้ใช้ค่า Stamina ที่ต่างกัน แต่ละปุ่มจะดูดค่าพลังงาน (Stamina) และเพิ่มความก้าวหน้า (Growth Progress) ไม่เท่ากัน 
- เงิน (Money) จะได้รับกลับมาเมื่อปลูกเสร็จ ทำให้สามารถนำไปต่อยอดซื้อใน `ShopScreen` ได้

---
## ✨ คุณสมบัติตามข้อกำหนด Assignment
1. **Application:** เป็นอิสระและมีความไม่ซ้ำกันตามหัวข้อ **"เกมส์ปลูกดอกไม้ (Dream Garden)"**
2. **Kivy Framework:** ใช้ Kivy สมบูรณ์แบบ (ทั้งระดับกราฟิกและ KV lang)
3. **Widgets Requirement:** จำนวนรวม > 30 Widgets (ปัจจุบันใช้ 40+ ตัว)
4. **Callbacks Requirement:** จำนวนรวม > 10 Callbacks (ปัจจุบันทำไปมากกว่า 20 Callbacks)
5. **Version Control:** มี Repository ของ Git ติดมาพ่วงด้วย 50 Commits ครอบคลุมระยะเวลา 14 วัน (ใช้หลัก Commit Early, Commit Often)
6. **Documentation:** อธิบายตาม README.md นี้ครบถ้วนและสมบูรณ์
