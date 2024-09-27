#multistage docker file
FROM node:20 as build
# as bulid = naming the stage

WORKDIR /app

COPY . .

RUN npm install
RUN npm run build


FROM nginx:stable-alpine as productioning
# productioning = naming the stage

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
#overwriting the /etc/nginx/nginx.conf with nginx.conf written by us


EXPOSE 80


CMD [ "nginx", "-g", "daemon off;" ]
# ("-g" run as a global container) ("daemon off" nginx will run as a foreground operation)