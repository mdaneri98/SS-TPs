package models;


public class Pair<T, V> {

    private T left;
    private V right;

    public Pair(T left, V right) {
        this.left = left;
        this.right = right;
    }

    public T getLeft() {
        return left;
    }

    public void setLeft(T left) {
        this.left = left;
    }

    public V getRight() {
        return right;
    }

    public void setRight(V right) {
        this.right = right;
    }

}
