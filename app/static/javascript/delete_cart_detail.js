document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.delete-cart-detail').forEach(button => {
            button.addEventListener('click', function () {
                const cart_detail_id = this.getAttribute("cart_detail_id");
                fetch(`/delete/cart/${cart_detail_id}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                })
                    .then(response => {
                        if (response.ok || response.status === 204) {
                            location.reload();
                        } else {
                            throw new Error('Không thể xóa khỏi giỏ hàng!');
                        }
                    })
                    .catch(error => {
                        console.error(error);
                        alert('Có lỗi xảy ra khi xóa khỏi giỏ hàng.');
                    });
            });
        });
    });