export type Vector2<T> = [T, T];
export type Vector3<T> = [T, T, T];
export type Vector4<T> = [T, T, T, T];
export type Vector5<T> = [T, T, T, T, T];
export type Vector6<T> = [T, T, T, T, T, T];

export type Annotation = {
  id: number;
  category_id: number;
  label: string; // fallback if category_id has no match
  bbox: Vector4<number>;
};

export type Category = {
  id: number;
  name: string;
};
