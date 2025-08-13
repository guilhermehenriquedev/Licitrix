// Configuração do Stripe para o frontend
export const STRIPE_CONFIG = {
  publishableKey: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || 'pk_test_...',
  priceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_ID || 'price_...',
}

// Função para carregar o Stripe
export const loadStripe = async () => {
  if (typeof window === 'undefined') return null
  
  try {
    const { loadStripe: loadStripeLib } = await import('@stripe/stripe-js')
    return await loadStripeLib(STRIPE_CONFIG.publishableKey)
  } catch (error) {
    console.error('Erro ao carregar Stripe:', error)
    return null
  }
}

// Função para criar checkout session
export const createCheckoutSession = async (successUrl: string, cancelUrl: string) => {
  try {
    const response = await fetch('/api/users/subscription/create-checkout-session/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: JSON.stringify({
        success_url: successUrl,
        cancel_url: cancelUrl,
      }),
    })

    if (!response.ok) {
      throw new Error('Erro ao criar sessão de checkout')
    }

    return await response.json()
  } catch (error) {
    console.error('Erro ao criar checkout session:', error)
    throw error
  }
}

// Função para redirecionar para checkout
export const redirectToCheckout = async (successUrl: string, cancelUrl: string) => {
  try {
    const stripe = await loadStripe()
    if (!stripe) {
      throw new Error('Stripe não pôde ser carregado')
    }

    const session = await createCheckoutSession(successUrl, cancelUrl)
    
    const { error } = await stripe.redirectToCheckout({
      sessionId: session.session_id,
    })

    if (error) {
      throw error
    }
  } catch (error) {
    console.error('Erro ao redirecionar para checkout:', error)
    throw error
  }
}
