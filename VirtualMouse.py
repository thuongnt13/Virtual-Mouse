import cv2
import HandTracking as htm
import pyautogui
import  numpy as np
import pytesseract

# Cài đặt đường dẫn của tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
image = cv2.imread(r'C:/Users/HACOM/OneDrive/Desktop/huongdan.png')


# Chuyển frame sang ảnh đen trắng để tăng độ chói cho việc nhận diện text
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
text = pytesseract.image_to_string(gray, lang='vie')
print(text)
with open("huongdan.txt", "a",encoding="utf-8") as f:
    f.writelines(text)

cam = cv2.VideoCapture(0)

detector = htm.handDetector(maxHands=1)

fingers_number = [4,8,12,16,20]

# các giá trị để làm min
smoothening = 5
plocX, plocY = 0, 0
clocX, clocY = 0, 0

# chiều rộng và chiều cao của camera
wCam,hCam =  680,480
# chiều rông và chiều cao của màn hình máy tính
wScreen,hScreen =  pyautogui.size()

drag = False

while True:
    success, frame = cam.read()

    # lật ngược lại camera
    image = cv2.flip(frame,1)
    
  
    # xác định vị trí bàn tay trên webcam 
    image = detector.findHands(image)
    lamark_list = detector.findPosition(image,draw=False)
    
    # kiểm tra sự tồn tại của bàn tay
    if len(lamark_list)!=0:
        # xác định tọa độ ngón trỏ
        x1,y1=lamark_list[8][1:]

        # xác định  sự co duỗi của các ngón tay
        fingers = [] # [0,1,0,0,0]
        # xác định ngón cái
        if lamark_list[fingers_number[0]][1] < lamark_list[fingers_number[0]-1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # xác định 4 ngón còn lại
        for id_finger in range(1,5):
            if lamark_list[fingers_number[id_finger]][2] < lamark_list[fingers_number[id_finger]-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        # vẽ 1 HCN nhỏ trên cam tượng trưng cho  với màn hình máy tính
        cv2.rectangle(image,(100,50),(wCam-100,hCam-190),(0,0,0),2)  

        # Chuyên đổi tọa độ của  ngón trỏ  trên màn hình webcam để tương ứng với màn hình máy tính 
        x3=np.interp(x1,(100,wCam-100),(0,wScreen))
        y3=np.interp(y1,(50,hCam-190),(0,hScreen))

        # Làm mịn các giá trị
        clocX = plocX + (x3 - plocX) / smoothening
        clocY = plocY + (y3 - plocY) / smoothening

        # tắt dữ chuột trái
        if drag == True and fingers.count(0) != 5:
            drag = False
            pyautogui.mouseUp(button = "left")

        # Chỉ ngón trỏ có Chế độ di chuyển
        if  fingers[0]==0 and fingers[1]==1 and fingers[2]==0 and fingers[3]==0 and fingers[4]==0:            
            pyautogui.moveTo(clocX,clocY)
            cv2.circle(image,(x1,y1),10,(0,255,0),-1)  
            plocX, plocY = clocX, clocY

      
        # Click chuột trái khi chỉ có ngón trỏ , ngón giữa , ngón cái được duỗi và khoảng cách < 27      
        elif fingers[0]==1 and fingers[1]==1 and fingers[2]==1 and fingers[3]==0  and fingers[4]== 0:
            # Tìm khoảng cách giữa các ngón tay
            length, img, lineInfo = detector.findDistance(8, 12, image) 
            if length < 27:
                cv2.circle(image,(lineInfo[4],lineInfo[5]),10,(0,255,0),-1)
                pyautogui.click()
                
        # Click chuột phải khi chỉ có ngón trỏ , ngón giữa , ngón út được duỗi  và khoảng cách < 27      
        elif fingers[0]==0 and fingers[1]==1 and fingers[2]==1 and fingers[3]==0  and fingers[4]== 1:
           # Tìm khoảng cách giữa các ngón tay
            length, img, lineInfo = detector.findDistance(8, 12, image)    
            if length < 27:
                cv2.circle(image,(lineInfo[4],lineInfo[5]),10,(0,255,0),-1)
                pyautogui.click(button="right")   

        # doubleClick chuột khi chỉ có ngón trỏ , ngón giữa được duỗi  và khoảng cách < 27
        elif fingers[1]==1 and fingers[2]==1 and fingers.count(0) == 3:
            # Tìm khoảng cách giữa các ngón tay
            length, img, lineInfo = detector.findDistance(8, 12, image)
            if length < 27:
                cv2.circle(image,(lineInfo[4],lineInfo[5]),10,(0,255,0),-1)
                pyautogui.doubleClick()

        # cuộn chuột lên khi chỉ có ngón cái , ngón trỏ được duỗi 
        elif fingers[0]==1 and fingers[1]==1 and fingers[2]==0 and fingers[3]==0 and fingers[4]==0:
            pyautogui.scroll(100)

        # cuộn chuột xuống  khi chỉ có ngón trỏ , ngón út được duỗi 
        elif fingers[0]==0 and fingers[1]==1 and fingers[2]==0 and fingers[3]==0 and fingers[4]==1:
            pyautogui.scroll(-100)                                 

        # kéo thả chuột khi bàn tay lắm lại
        elif fingers.count(0) == 5:
            if not drag : 
                drag = True
                pyautogui.mouseDown(button = "left") 
            pyautogui.moveTo(clocX,clocY)
            plocX, plocY = clocX, clocY



    # hiện thị camera
    cv2.imshow("Virtual Mouse" ,image)
    # màn hình camera luôn được hiển thị trên cùng
    cv2.setWindowProperty("Virtual Mouse",cv2.WND_PROP_TOPMOST,1)
    # tắt chương trình khi nhấn "q"
    if cv2.waitKey(1) == ord("q"):
        break
cam.release()
cv2.destroyAllWindows()    
