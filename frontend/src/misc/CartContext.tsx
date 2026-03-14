import { createContext, useContext, useState, type ReactNode } from "react";
import { Option } from '../misc/misc';

interface CartItem{
    id: number;
    quantity: number;
}

interface CartContextType{
    cart: CartItem[];
    addToCart: (id: number) => void;
    removeFromCart: (id: number) => void;
    getCartCount: () => number;
}

const CartContext = createContext<Option<CartContextType>>(Option.none());

export function CartProvider({ children }: { children: ReactNode }){
    const [cart, setCart] = useState<CartItem[]>([]);

    const addToCart = (id: number)=> {
        setCart(prev =>{
            const existing = prev.find(item => item.id === id);

            if(existing){
                return prev.map(item =>
                    item.id === id
                    ? {...item, quantity: item.quantity + 1}
                    : item
                );
            }
            return [...prev, {id, quantity: 1}];
        });
    };
    const removeFromCart = (id: number) => { // remove from cart currently takes every instance of the item out of the cart not individual 
        setCart(prev => prev.filter(item => item.id !== id));
    };
    const getCartCount = () =>
        cart.reduce((total,item) => total + item.quantity, 0);
    return(
        <CartContext.Provider value={Option.some({cart, addToCart, removeFromCart, getCartCount})}>
            {children}
        </CartContext.Provider>
    );
}

export function useCart(){
    const context = useContext(CartContext);
    if(!context){
        throw new Error("useCart must be used within CartProvider");    
    }
    return context;
}