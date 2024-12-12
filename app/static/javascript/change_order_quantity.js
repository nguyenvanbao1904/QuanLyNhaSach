document.addEventListener('DOMContentLoaded', function () {
        const quantityInputs = document.querySelectorAll('#typeNumber');
        let debounceTimer;

        quantityInputs.forEach(input => {
            input.addEventListener('input', function (event) {
                const quantityInput = event.target;
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    const newQuantity = parseInt(quantityInput.value);

                    if (isNaN(newQuantity) || newQuantity < 1) {
                        quantityInput.value = 1;
                    }

                    changeQuantity(quantityInput);
                }, 500);
            });
        });
    });

    function changeQuantity(inputElement) {
        const newQuantity = parseInt(inputElement.value);
        const cartDetailId = inputElement.getAttribute('cart_detail_id');

        console.log(`Số lượng mới: ${newQuantity}, cart_detail_id: ${cartDetailId}`);

        fetch('/update-cart', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                cart_detail_id: cartDetailId,
                quantity: newQuantity,
            }),
        })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Không thể cập nhật giỏ hàng!');
                }
            })
            .then(data => {
                console.log(data.message);
                location.reload();
            })
            .catch(error => {
                console.error(error);
                alert('Có lỗi xảy ra khi cập nhật giỏ hàng.');
            });
    }