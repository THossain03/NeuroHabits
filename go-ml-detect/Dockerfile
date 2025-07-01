FROM golang:1.21-alpine as builder
WORKDIR /app
COPY . .
RUN go build -o ml_detect main.go

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/ml_detect .
EXPOSE 9000
CMD ["./ml_detect"] 