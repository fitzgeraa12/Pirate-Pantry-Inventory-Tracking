import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
// import { Option } from '../misc/misc';

interface CartItem{
    id: number;
    name: string;
    quantity: number;
}

interface CartContextType{
    cart: CartItem[]; 
    addToCart: (id: number) => void;
    removeFromCart: (id: number) => void;
    getCartCount: () => number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }){
    const [cart, setCart] = useState<CartItem[]>([]);

    useEffect(() => {
      console.log("Cart updated:", cart);
    }, [cart]);

    const addToCart = (id: number, name: string, maxQuantity: number)=> {
        setCart(prev =>{
            const existing = prev.find(item => item.id === id);
            // If more than in inventory is attempted to be added, deny it 
            if(existing && existing.quantity >= maxQuantity) {
                return prev;
            }
            //otherwise add an instance
            if(existing){
                return prev.map(item =>
                    item.id === id
                    ? {...item, name, quantity: item.quantity + 1}
                    : item
                );
            }
            return [...prev, {id, name, quantity: 1}];
        });
    };
    const removeFromCart = (id: number) => { // remove from cart currently takes every instance of the item out of the cart not individual 
        setCart(prev =>{
            const existing =  prev.find(item => item.id == id);
            //If item is not in cart do nothing
            if(!existing) return prev;
            //If it item count 
            if(existing.quantity === 1){
                return prev.filter(item => item.id !==id);
            }
            //Otherwise remove one instance of item
            return prev.map(item =>
                item.id === id
                ? {...item, quantity: item.quantity - 1}
                : item
            );
        });
    };
    const getCartCount = () =>
        cart.reduce((total,item) => total + item.quantity, 0);
    const clearCart = () => {
        setCart([]);
    }

    return(
        <CartContext.Provider value={{cart, addToCart, removeFromCart, getCartCount, clearCart}}>
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