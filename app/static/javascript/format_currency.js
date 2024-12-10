document.addEventListener('DOMContentLoaded', () => {
        const priceElements = document.querySelectorAll('.price');
        priceElements.forEach(priceElement => {
            const rawPrice = parseFloat(priceElement.getAttribute('data-price'));
            if (!isNaN(rawPrice)) {
                const formattedPrice = new Intl.NumberFormat('vi-VN', {
                    style: 'currency',
                    currency: 'VND',
                    minimumFractionDigits: 0
                }).format(rawPrice);
                priceElement.textContent = formattedPrice;
            }
        });
    });