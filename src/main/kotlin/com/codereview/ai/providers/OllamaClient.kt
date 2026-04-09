package com.codereview.ai.providers

import com.codereview.ai.AiClient
import com.codereview.ai.AiConfig
import com.codereview.ai.AiFinding
import com.codereview.ai.AiResponse
import com.codereview.ai.AiFindingParser
import com.codereview.ai.TestResponse
import kotlinx.serialization.json.*
import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

internal class OllamaClient(private val config: AiConfig) : AiClient {
    private val json = Json { ignoreUnknownKeys = true }
    private val client = OkHttpClient.Builder()
        .connectTimeout(config.timeoutSeconds.toLong(), TimeUnit.SECONDS)
        .readTimeout(config.timeoutSeconds.toLong(), TimeUnit.SECONDS)
        .build()

    override suspend fun review(prompt: String, codeContent: String): AiResponse {
        return try {
            val fullPrompt = "$prompt\n\n代码内容：\n$codeContent"

            val requestBody = buildJsonObject {
                put("model", config.model)
                put("prompt", fullPrompt)
                put("stream", false)
                put("options", buildJsonObject {
                    put("num_predict", config.maxTokens)
                })
            }

            val mediaType = "application/json".toMediaType()
            val body = requestBody.toString().toRequestBody(mediaType)

            val cleanedApiUrl = config.apiUrl.trim()
            val fullApiUrl = if (cleanedApiUrl.endsWith("/")) "${cleanedApiUrl}api/generate" else if (cleanedApiUrl.contains("/api/")) cleanedApiUrl else "${cleanedApiUrl}/api/generate"
            val httpUrl = fullApiUrl.toHttpUrl()
            val request = Request.Builder()
                .url(httpUrl)
                .post(body)
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string() ?: return AiResponse(
                success = false,
                findings = emptyList(),
                errorMessage = "Empty response from Ollama"
            )

            if (!response.isSuccessful) {
                return AiResponse(
                    success = false,
                    findings = emptyList(),
                    errorMessage = "Ollama API error: ${response.code} $responseBody"
                )
            }

            parseOllamaResponse(responseBody)
        } catch (e: Exception) {
            AiResponse(
                success = false,
                findings = emptyList(),
                errorMessage = e.message
            )
        }
    }

    private fun parseOllamaResponse(responseJson: String): AiResponse {
        val root = try {
            json.parseToJsonElement(responseJson).jsonObject
        } catch (e: Exception) {
            return AiResponse(
                success = false,
                findings = emptyList(),
                errorMessage = "JSON parse error: ${e.message}, input: ${responseJson.take(200)}..."
            )
        }

        val text = root["response"]?.toString()?.removeSurrounding("\"") ?: return AiResponse(
            success = false,
            findings = emptyList(),
            errorMessage = "No response content"
        )

        val parseResult = AiFindingParser.parseFindings(text)
        val debugInfo = "$responseJson\n\n[Parsed: ${parseResult.findings.size} findings, Expected: ${parseResult.expectedTotal}, Found tag: ${parseResult.foundTag}]"
        val cleanedRawResponse = debugInfo.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()
        return AiResponse(
            success = true,
            findings = parseResult.findings,
            expectedTotal = parseResult.expectedTotal,
            parsingDebug = parseResult.debugLog,
            rawResponse = cleanedRawResponse
        )
    }

    override suspend fun testConnection(prompt: String): TestResponse {
        return try {
            val requestBody = buildJsonObject {
                put("model", config.model)
                put("prompt", prompt)
                put("stream", false)
                put("options", buildJsonObject {
                    put("num_predict", config.maxTokens)
                })
            }

            val mediaType = "application/json".toMediaType()
            val body = requestBody.toString().toRequestBody(mediaType)

            val cleanedApiUrl = config.apiUrl.trim()
            val apiUrl = if (cleanedApiUrl.endsWith("/")) {
                "${cleanedApiUrl}api/generate"
            } else if (cleanedApiUrl.contains("/api/")) {
                cleanedApiUrl
            } else {
                "${cleanedApiUrl}/api/generate"
            }

            val httpUrl = apiUrl.toHttpUrl()
            val request = Request.Builder()
                .url(httpUrl)
                .post(body)
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string()
                ?: return TestResponse(
                    success = false,
                    responseText = "",
                    errorMessage = "Empty response from Ollama",
                    rawResponse = null
                )

            if (!response.isSuccessful) {
                val cleanedRawResponse = responseBody.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()
                return TestResponse(
                    success = false,
                    responseText = "",
                    errorMessage = "API error: ${response.code}",
                    rawResponse = cleanedRawResponse
                )
            }

            val root = try {
                json.parseToJsonElement(responseBody).jsonObject
            } catch (e: Exception) {
                return TestResponse(
                    success = false,
                    responseText = "",
                    errorMessage = "JSON parse error: ${e.message}",
                    rawResponse = responseBody.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()
                )
            }

            val text = root["response"]?.toString()
                ?.removeSurrounding("\"")
                ?: return TestResponse(
                    success = false,
                    responseText = "",
                    errorMessage = "No response content",
                    rawResponse = responseBody.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()
                )

            val cleanedRawResponse = responseBody.replace("\\n", " ").replace("\\s+".toRegex(), " ").trim()
            TestResponse(
                success = true,
                responseText = text,
                errorMessage = null,
                rawResponse = cleanedRawResponse
            )
        } catch (e: Exception) {
            TestResponse(
                success = false,
                responseText = "",
                errorMessage = e.message,
                rawResponse = null
            )
        }
    }
}
