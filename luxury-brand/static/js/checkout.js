// Initialize Stripe
const stripe = Stripe('{{ config.STRIPE_PUBLIC_KEY }}');
let elements;

// Initialize payment on page load
document.addEventListener('DOMContentLoaded', function() {
    initializePayment();
    
    // Handle payment method change
    document.querySelectorAll('input[name="payment_method"]').forEach(radio => {
        radio.addEventListener('change', function() {
            togglePaymentMethods(this.value);
        });
    });
});

function initializePayment() {
    // Check which payment method is selected
    const selectedMethod = document.querySelector('input[name="payment_method"]:checked').value;
    togglePaymentMethods(selectedMethod);
}

function togglePaymentMethods(method) {
    if (method === 'credit_card') {
        document.getElementById('payment-element').style.display = 'block';
        document.getElementById('paypal-button-container').style.display = 'none';
        initializeStripe();
    } else if (method === 'paypal') {
        document.getElementById('payment-element').style.display = 'none';
        document.getElementById('paypal-button-container').style.display = 'block';
        initializePayPal();
    }
}

async function initializeStripe() {
    // Fetch payment intent from server
    const response = await fetch('/api/create-payment-intent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            order_id: window.orderId, // You'll need to set this
            amount: window.totalAmount // You'll need to set this
        }),
    });
    
    const { clientSecret, payment_id } = await response.json();
    
    // Initialize Stripe Elements
    const appearance = {
        theme: 'stripe',
    };
    elements = stripe.elements({ appearance, clientSecret });
    
    const paymentElement = elements.create('payment');
    paymentElement.mount('#payment-element');
    
    // Handle form submission
    const form = document.getElementById('checkout-form');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        const { error } = await stripe.confirmPayment({
            elements,
            confirmParams: {
                return_url: `${window.location.origin}/order-confirmation`,
            },
        });
        
        if (error) {
            const messageContainer = document.querySelector('#error-message');
            messageContainer.textContent = error.message;
        }
    });
}

function initializePayPal() {
    paypal.Buttons({
        createOrder: function(data, actions) {
            return fetch('/api/create-paypal-payment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    order_id: window.orderId,
                    amount: window.totalAmount
                }),
            })
            .then(res => res.json())
            .then(data => data.paymentID);
        },
        onApprove: function(data, actions) {
            return fetch('/api/execute-paypal-payment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    paymentID: data.paymentID,
                    payerID: data.payerID
                }),
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/order-confirmation';
                } else {
                    alert('Payment failed: ' + data.error);
                }
            });
        }
    }).render('#paypal-button-container');
}