<div align="center">
  <h1>CARO GAME WITH MINIMAX ALGORITHM</h1>
</div>

## Thuật toán Minimax:
  - Là thuật toán đệ quy lựa chọn bước tiếp theo trong một trò chơi có hai người bằng cách định giá trị cho các Node trên cây trò chơi sau đó tìm Node có giá trị phụ hợp để đi bước tiếp theo.
  - Hai người chơi trong trò chơi được đại diện là MAX và MIN. MAX đại diện cho người chơi luôn muốn dành thắng lợi và cố gắng tối ưu hóa ưu thế của mình. Ngược lại, MIN lại cố gắng giảm điểm số của MAX. Giải thuật Minimax thể hiện bằng cách định trị các Node trên cây trò chơi: Node thuộc lớp MAX thì gán cho nó giá trị lớn nhất của con Node đó. Node thuộc lớp MIN thì gán cho nó giá trị nhỏ nhất của con Node đó. Từ các giá trị này người chơi sẽ lựa chọn cho mình nước đi tiếp theo hợp lý nhất.

  - Giải thuật Minimax thể hiện bằng cách định trị các Node trên cây trò chơi:
    + Node thuộc lớp MAX thì gán cho nó giá trị lớn nhất của con Node đó.
    + Node thuộc lớp MIN thì gán cho nó giá trị nhỏ nhất của con Node đó. Từ các giá trị này người chơi sẽ lựa chọn cho mình nước đi tiếp theo hợp lý nhất.
    + Nếu như đạt đến giới hạn tìm kiếm (đến tầng dưới cùng của cây tìm kiếm tức là trạng thái kết thúc của trò chơi).
    + Tính giá trị của thế cờ hiện tại ứng với người chơi ở đó. Ghi nhớ kết quả.
    + Nếu như mức đang xét là của người chơi cực tiểu (nút MIN), áp dụng thủ tục Minimax này cho các con của nó. Ghi nhớ kết quả nhỏ nhất.
    + Nếu như mức đang xét là của người chơi cực đại (nút MAX), áp dụng thủ tục Minimax này cho các con của nó. Ghi nhớ kết quả lớn nhất.
  
## Thuật toán cắt tỉa Alpha-Beta.
  - Để tối ưu thuật toán Minimax nên ta sẽ bỏ những nút không tối ưu bằng thuật toán cắt tỉa Alpha-Beta.
  - Ý tưởng: 
    + Nếu một nhánh tìm kiếm nào đó không thể cải thiện với giá trị mà chúng ta đã có, thì không cần xét đến hàm đó nữa.<br>
    -> tiết kiệm chi phí thời gian, bộ nhớ cho cây tìm kiếm.
    + Dùng hai cận Alpha và Beta để so sánh và loại bỏ các trường hợp sẽ không cần xét đến trong thuật toán Minimax.
  - Mô tả: 
    + Alpha lưu nước đi tốt nhất của máy, Beta lưu giá trị tốt nhất của player
 -  Nếu bất cứ khi nào Alpha >= Beta, thì player chắc chắn sẽ chọn nước đi tốt nhất cho họ và ép nước đi tệ hơn Alpha cho máy, vì vậy mà không cần xét thêm bước nào nữa.


