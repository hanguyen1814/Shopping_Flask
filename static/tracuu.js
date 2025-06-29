document.addEventListener("DOMContentLoaded", async () => {
  try {
    // Lấy giá trị shopid và itemid từ thuộc tính của phần tử DOM hoặc sử dụng giá trị mặc định
    const shopid =
      document.querySelector(".info-img")?.getAttribute("shopid") ||
      "defaultShop";
    const itemid =
      document.querySelector(".info-img")?.getAttribute("itemid") ||
      "defaultItem";

    if (shopid != "defaultShop" && itemid != "defaultItem") {
      const reviews = document.querySelector(".reviews");
      reviews.style.display = "block";
      // Tạo URL API
      const url = `https://script.google.com/macros/s/AKfycbwfQxP0aYAUMfx_J_TdNEMKBGkYgvFg0EGMiS2zTqFx7rUUYc5XtJLySVF6CAb3TuKH/exec?shopid=${shopid}&itemid=${itemid}`;

      // Gửi yêu cầu API và chờ dữ liệu trả về
      const response = await fetch(url);
      const jsonResponse = await response.json();

      const reviewContainer = document.querySelector(".data-table tbody");

      // Xóa dữ liệu cũ (nếu có)
      reviewContainer.innerHTML = "";
      // Kiểm tra nếu dữ liệu trả về hợp lệ
      const ratingCounts = jsonResponse.data.data;
      if (!ratingCounts || ratingCounts.key === "") {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 2; // Gộp cột
        cell.textContent = "Sản phẩm không có đánh giá hoặc phân loại!";
        row.appendChild(cell);
        reviewContainer.appendChild(row);
        return; // Thoát khỏi hàm nếu không có dữ liệu
      }

      // Duyệt qua từng mục trong dữ liệu và thêm vào bảng
      Object.entries(ratingCounts).forEach(([key, value]) => {
        const row = document.createElement("tr");
        const productCell = document.createElement("td");
        const countCell = document.createElement("td");

        productCell.textContent = key; // Tên sản phẩm
        countCell.textContent = value; // Số lượng đánh giá

        row.appendChild(productCell);
        row.appendChild(countCell);
        reviewContainer.appendChild(row);
      });
    }
  } catch (error) {
    console.error("Error fetching review data:", error);
  }
});
