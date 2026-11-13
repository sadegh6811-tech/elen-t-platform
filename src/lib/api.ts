export const apiFetch = (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem("elen_token");
  const headers = {
    ...options.headers,
    ...(token ? { "Authorization": `Bearer ${token}` } : {})
  };
  return fetch(url, { ...options, headers });
};
