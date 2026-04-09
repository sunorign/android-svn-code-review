package com.codereview.ai

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.put
import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

/**
 * Client for getting embedding vectors from text.
 */
interface EmbeddingClient {
    suspend fun embed(text: String): Result<FloatArray>
}

/**
 * Ollama implementation of EmbeddingClient using Ollama's /api/embeddings endpoint.
 */
class OllamaEmbeddingClient(private val config: AiConfig) : EmbeddingClient {
    private val json = Json { ignoreUnknownKeys = true }
    private val client = OkHttpClient.Builder()
        .connectTimeout(config.timeoutSeconds.toLong(), TimeUnit.SECONDS)
        .readTimeout(config.timeoutSeconds.toLong(), TimeUnit.SECONDS)
        .build()

    override suspend fun embed(text: String): Result<FloatArray> {
        return try {
            val requestBody = buildJsonObject {
                put("model", config.model)
                put("prompt", text)
            }

            val mediaType = "application/json".toMediaType()
            val body = requestBody.toString().toRequestBody(mediaType)

            val cleanedApiUrl = config.apiUrl.trim()
            // Ollama embedding endpoint is /api/embeddings
            val fullApiUrl = when {
                cleanedApiUrl.endsWith("/") -> "${cleanedApiUrl}api/embeddings"
                cleanedApiUrl.contains("/api/") -> {
                    // If it already has /api/, replace the end with embeddings
                    cleanedApiUrl.replace(Regex("/generate$"), "/embeddings")
                }
                else -> "${cleanedApiUrl}/api/embeddings"
            }

            val httpUrl = fullApiUrl.toHttpUrl()
            val request = Request.Builder()
                .url(httpUrl)
                .post(body)
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string()
                ?: return Result.failure(IllegalStateException("Empty response from Ollama"))

            if (!response.isSuccessful) {
                return Result.failure(
                    IllegalStateException("Ollama API error: ${response.code} $responseBody")
                )
            }

            // Parse embedding array from response
            val root = json.parseToJsonElement(responseBody).jsonObject
            val embeddingArray = root["embedding"]?.jsonArray
                ?: return Result.failure(IllegalStateException("No embedding field in response"))

            val embedding = FloatArray(embeddingArray.size) { index ->
                embeddingArray[index].jsonPrimitive.content.toFloat()
            }

            Result.success(embedding)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
